-- 서울시 제공 예정 원천 데이터를 경로 ETA·환승시간에 참고하기 위한 테이블.
-- 1) 버스노선별 정류장별 시간대별 승하차 인원
-- 2) 정류장(역사)별 사용자유형별 환승 승객수 및 환승시간
-- 표준버스정류장ID ↔ places.standard_bus_stop_id / 정류장·역사 ID ↔ subway_stations.card_stop_id

ALTER TABLE places
    ADD COLUMN IF NOT EXISTS standard_bus_stop_id VARCHAR(20),
    ADD COLUMN IF NOT EXISTS ars_id VARCHAR(10);
CREATE INDEX IF NOT EXISTS idx_places_std_stop ON places (standard_bus_stop_id);
CREATE INDEX IF NOT EXISTS idx_places_ars ON places (ars_id);
COMMENT ON COLUMN places.standard_bus_stop_id IS '서울 표준버스정류장ID (버스 시간대별 승하차.standard_stop_id)';
COMMENT ON COLUMN places.ars_id IS '버스정류장ARS번호';

ALTER TABLE subway_stations
    ADD COLUMN IF NOT EXISTS card_stop_id VARCHAR(20);
CREATE INDEX IF NOT EXISTS idx_stations_card_stop ON subway_stations (card_stop_id);
COMMENT ON COLUMN subway_stations.card_stop_id IS '교통카드 정류장/역사 ID (환승통계.alight_stop_id, board_stop_id)';

ALTER TABLE subway_station_transfers
    ADD COLUMN IF NOT EXISTS avg_transfer_s INT,
    ADD COLUMN IF NOT EXISTS sample_transfers INT;
COMMENT ON COLUMN subway_station_transfers.avg_transfer_s IS '환승통계 환승_시간_평균(초) 최근값';

CREATE TABLE IF NOT EXISTS bus_hourly_boardings (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    use_ym                  CHAR(6) NOT NULL,           -- 사용년월 YYYYMM
    route_no                VARCHAR(20) NOT NULL,       -- 노선번호
    route_name              VARCHAR(100),               -- 노선명
    standard_stop_id        VARCHAR(20) NOT NULL,       -- 표준버스정류장ID
    ars_id                  VARCHAR(10),                -- 버스정류장ARS번호
    stop_name               VARCHAR(100),               -- 역명(정류장명)
    boarding_h00 INT, alight_h00 INT,
    boarding_h01 INT, alight_h01 INT,
    boarding_h02 INT, alight_h02 INT,
    boarding_h03 INT, alight_h03 INT,
    boarding_h04 INT, alight_h04 INT,
    boarding_h05 INT, alight_h05 INT,
    boarding_h06 INT, alight_h06 INT,
    boarding_h07 INT, alight_h07 INT,
    boarding_h08 INT, alight_h08 INT,
    boarding_h09 INT, alight_h09 INT,
    boarding_h10 INT, alight_h10 INT,
    boarding_h11 INT, alight_h11 INT,
    boarding_h12 INT, alight_h12 INT,
    boarding_h13 INT, alight_h13 INT,
    boarding_h14 INT, alight_h14 INT,
    boarding_h15 INT, alight_h15 INT,
    boarding_h16 INT, alight_h16 INT,
    boarding_h17 INT, alight_h17 INT,
    boarding_h18 INT, alight_h18 INT,
    boarding_h19 INT, alight_h19 INT,
    boarding_h20 INT, alight_h20 INT,
    boarding_h21 INT, alight_h21 INT,
    boarding_h22 INT, alight_h22 INT,
    boarding_h23 INT, alight_h23 INT,
    transport_type_code     VARCHAR(10),                -- 교통수단타입코드
    transport_type_name     VARCHAR(50),                -- 교통수단타입명
    registered_on           DATE,                       -- 등록일자
    place_id                UUID REFERENCES places(id) ON DELETE SET NULL,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (use_ym, route_no, standard_stop_id)
);
CREATE INDEX IF NOT EXISTS idx_bus_hourly_stop ON bus_hourly_boardings (standard_stop_id, use_ym DESC);
CREATE INDEX IF NOT EXISTS idx_bus_hourly_route ON bus_hourly_boardings (route_no, use_ym DESC);
CREATE INDEX IF NOT EXISTS idx_bus_hourly_place ON bus_hourly_boardings (place_id);
COMMENT ON TABLE bus_hourly_boardings IS '버스노선별 정류장별 시간대별 승하차 인원. boarding_hNN=N시승차총승객수, alight_hNN=N시하차총승객수';

CREATE TABLE IF NOT EXISTS station_transfer_flows (
    id                          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    base_date                   DATE NOT NULL,              -- 기준_날짜
    alight_stop_id              VARCHAR(20) NOT NULL,       -- 하차_정류장/역사_ID
    board_stop_id               VARCHAR(20) NOT NULL,       -- 승차_정류장/역사_ID
    hour                        SMALLINT NOT NULL,          -- 시간대 0-23
    transfer_count_total        INT NOT NULL DEFAULT 0,     -- 환승_수_합
    transfer_count_general      INT NOT NULL DEFAULT 0,     -- 일반
    transfer_count_child        INT NOT NULL DEFAULT 0,     -- 어린이
    transfer_count_youth        INT NOT NULL DEFAULT 0,     -- 청소년
    transfer_count_senior       INT NOT NULL DEFAULT 0,     -- 경로
    transfer_count_disabled     INT NOT NULL DEFAULT 0,     -- 장애인
    transfer_time_avg_s         INT,                        -- 환승_시간_평균 (초)
    transfer_time_avg_general_s INT,
    transfer_time_avg_child_s   INT,
    transfer_time_avg_youth_s   INT,
    transfer_time_avg_senior_s  INT,
    transfer_time_avg_disabled_s INT,
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (base_date, alight_stop_id, board_stop_id, hour),
    CONSTRAINT ck_transfer_hour CHECK (hour BETWEEN 0 AND 23)
);
CREATE INDEX IF NOT EXISTS idx_transfer_flow_pair
    ON station_transfer_flows (alight_stop_id, board_stop_id, hour, base_date DESC);
CREATE INDEX IF NOT EXISTS idx_transfer_flow_alight
    ON station_transfer_flows (alight_stop_id, hour);
COMMENT ON TABLE station_transfer_flows IS '서울시 정류장별 사용자유형별 환승 승객수 및 환승시간. 환승 도보 구간에 참고';
