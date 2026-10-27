from app.services.demand_service import _congestion, _dwell_s
from app.models.bus_hourly_boarding import BusHourlyBoarding


def test_congestion_scales_with_load():
    assert _congestion(10, 10) == 1
    assert _congestion(200, 200) == 3
    assert _congestion(800, 500) == 5


def test_dwell_caps_at_90s():
    assert _dwell_s(0) == 0
    assert _dwell_s(4000) == 90
    assert _dwell_s(80) == 2


def test_hourly_counts_accessor():
    row = BusHourlyBoarding(standard_stop_id="1", route_no="146", use_ym="202410")
    row.boarding_h08 = 120
    row.alight_h08 = 40
    assert row.counts_at(8) == (120, 40)
    assert row.counts_at(99) == (0, 0)
