from app.domain.geo import haversine_m, walk_seconds
from app.domain.messages import SAME_ORIGIN_DEST, OFF_ROUTE, TRANSFER_RISK
from app.domain.timing import (
    VehicleOption,
    pick_boardable,
    pick_transfer,
    remaining_seconds,
    off_route,
    should_alert,
    summarize_durations,
)


def test_walk_speed_changes_duration():
    assert walk_seconds(125, "normal") == 100
    assert walk_seconds(125, "fast") < walk_seconds(125, "slow")


def test_boarding_skips_too_soon_vehicle():
    vehicles = [VehicleOption(20), VehicleOption(90)]
    decision = pick_boardable(vehicles, walk_arrive_s=40, buffer_s=30)
    assert decision.boardable
    assert decision.vehicle.arrival_seconds == 90


def test_boarding_none_when_all_too_soon():
    decision = pick_boardable([VehicleOption(10)], walk_arrive_s=40, buffer_s=30)
    assert not decision.boardable


def test_transfer_risk_when_tight():
    decision = pick_transfer([VehicleOption(80)], alight_s=50, transfer_walk_s=20, buffer_s=30)
    assert decision.connected
    assert decision.risk


def test_transfer_fail_when_vehicle_already_gone():
    decision = pick_transfer([VehicleOption(40)], alight_s=50, transfer_walk_s=20, buffer_s=30)
    assert not decision.connected


def test_remaining_and_alerts():
    steps = [
        {"step_order": 1, "duration_s": 100},
        {"step_order": 2, "duration_s": 200},
    ]
    assert remaining_seconds(steps, 2, progress_s=50) == 150
    assert should_alert(120, 3)
    assert not should_alert(400, 3)
    assert off_route(200)
    assert not off_route(10)


def test_summarize_includes_transfer_walk():
    parts = summarize_durations([
        {"mode": "walk", "duration_s": 80, "transit_info": {}},
        {"mode": "bus", "duration_s": 500, "transit_info": {"wait_seconds": 100}},
        {"mode": "walk", "duration_s": 60, "transit_info": {}},
        {"mode": "subway", "duration_s": 400, "transit_info": {"wait_seconds": 50}},
        {"mode": "walk", "duration_s": 70, "transit_info": {}},
    ])
    assert parts["walk_duration_s"] == 150
    assert parts["transfer_walk_s"] == 60
    assert parts["wait_duration_s"] == 100
    assert parts["transfer_wait_s"] == 50
    assert parts["vehicle_duration_s"] == 750


def test_spec_messages_exist():
    assert SAME_ORIGIN_DEST
    assert OFF_ROUTE
    assert TRANSFER_RISK


def test_haversine_gangnam_seoul():
    meters = haversine_m(37.4979, 127.0276, 37.5547, 126.9707)
    assert 7000 < meters < 12000
