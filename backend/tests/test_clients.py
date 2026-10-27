from app.clients.seoul_subway import ARRIVAL_CODE_MAP, SUBWAY_LINE_MAP, parse_ordkey, parse_updn
from app.clients.tago import PORTAL_ERRORS, _as_list


def test_tago_item_list_wrappers():
    assert _as_list(None) == []
    assert _as_list({"item": {"nodeid": "A"}}) == [{"nodeid": "A"}]
    assert len(_as_list({"item": [{"nodeid": "A"}, {"nodeid": "B"}]})) == 2


def test_tago_portal_error_codes_from_spec():
    assert PORTAL_ERRORS["30"] == "SERVICE_KEY_IS_NOT_REGISTERED_ERROR"
    assert PORTAL_ERRORS["22"] == "LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR"


def test_subway_line_map_covers_spec_ids():
    assert SUBWAY_LINE_MAP["1001"] == "1호선"
    assert SUBWAY_LINE_MAP["1032"] == "GTX-A"
    assert SUBWAY_LINE_MAP["1077"] == "신분당선"
    assert len(SUBWAY_LINE_MAP) == 17


def test_subway_arrival_codes():
    assert ARRIVAL_CODE_MAP[0] == "진입"
    assert ARRIVAL_CODE_MAP[99] == "운행중"


def test_ordkey_and_updn_parsing():
    parsed = parse_ordkey("01015DEST0")
    assert parsed["ord_updn"] == "0"
    assert parsed["ord_seq"] == "1"
    assert parsed["ord_remaining_stops"] == 15
    assert parse_updn("하행") == 1
    assert parse_updn("0") == 0
