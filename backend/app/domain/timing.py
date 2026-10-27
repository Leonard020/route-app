from dataclasses import dataclass, field
from typing import Optional


@dataclass
class VehicleOption:
    arrival_seconds: int
    meta: dict = field(default_factory=dict)


@dataclass
class BoardingDecision:
    boardable: bool
    wait_seconds: Optional[int]
    vehicle: Optional[VehicleOption]
    reason: str


@dataclass
class TransferDecision:
    connected: bool
    wait_seconds: Optional[int]
    risk: bool
    vehicle: Optional[VehicleOption]
    reason: str


def pick_boardable(
    vehicles: list[VehicleOption],
    walk_arrive_s: int,
    buffer_s: int,
) -> BoardingDecision:
    ready_at = walk_arrive_s + buffer_s
    for vehicle in sorted(vehicles, key=lambda v: v.arrival_seconds):
        if vehicle.arrival_seconds >= ready_at:
            wait = max(vehicle.arrival_seconds - walk_arrive_s, 0)
            return BoardingDecision(True, wait, vehicle, "여유시간 확보")
    if vehicles:
        return BoardingDecision(False, None, None, "시간 부족")
    return BoardingDecision(False, None, None, "실시간 정보 미제공")


def pick_transfer(
    vehicles: list[VehicleOption],
    alight_s: int,
    transfer_walk_s: int,
    buffer_s: int,
) -> TransferDecision:
    arrive_stop = alight_s + transfer_walk_s
    ready_at = arrive_stop + buffer_s
    for vehicle in sorted(vehicles, key=lambda v: v.arrival_seconds):
        if vehicle.arrival_seconds >= ready_at:
            wait = max(vehicle.arrival_seconds - arrive_stop, 0)
            return TransferDecision(True, wait, False, vehicle, "환승 가능")
        if vehicle.arrival_seconds >= arrive_stop:
            wait = max(vehicle.arrival_seconds - arrive_stop, 0)
            return TransferDecision(True, wait, True, vehicle, "환승 위험")
    if vehicles:
        return TransferDecision(False, None, True, None, "환승 불가")
    return TransferDecision(False, None, False, None, "후속 차량 없음")


def remaining_seconds(steps: list[dict], current_step: int, progress_s: int = 0) -> int:
    total = 0
    for step in steps:
        order = int(step.get("step_order") or 0)
        duration = int(step.get("duration_s") or 0)
        if order < current_step:
            continue
        if order == current_step:
            total += max(duration - progress_s, 0)
        else:
            total += duration
    return total


def off_route(distance_from_path_m: float, threshold_m: float = 120.0) -> bool:
    return distance_from_path_m > threshold_m


def should_alert(remaining_s: int, minutes_before: int) -> bool:
    return 0 < remaining_s <= max(minutes_before, 1) * 60


def summarize_durations(steps: list[dict]) -> dict:
    walk = wait = vehicle = transfer_walk = transfer_wait = 0
    first_transit_seen = False
    for i, step in enumerate(steps):
        mode = step.get("mode")
        duration = int(step.get("duration_s") or 0)
        info = step.get("transit_info") or {}
        if mode == "walk":
            prev = steps[i - 1]["mode"] if i else None
            nxt = steps[i + 1]["mode"] if i + 1 < len(steps) else None
            if prev in ("bus", "subway") and nxt in ("bus", "subway"):
                transfer_walk += duration
            else:
                walk += duration
        elif mode in ("bus", "subway"):
            wait_s = int(info.get("wait_seconds") or 0)
            if not first_transit_seen:
                wait += wait_s
                first_transit_seen = True
            else:
                transfer_wait += wait_s
            vehicle += max(duration - wait_s, 0)
    return {
        "walk_duration_s": walk,
        "wait_duration_s": wait,
        "vehicle_duration_s": vehicle,
        "transfer_walk_s": transfer_walk,
        "transfer_wait_s": transfer_wait,
        "total_duration_s": walk + wait + vehicle + transfer_walk + transfer_wait,
    }
