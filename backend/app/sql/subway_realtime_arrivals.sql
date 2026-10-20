CREATE TABLE subway_realtime_arrivals (
    id                     UUID NOT NULL DEFAULT uuid_generate_v4(),
    recptn_dt              TIMESTAMPTZ NOT NULL,     -- recptnDt (도착정보 생성시각)
    fetched_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
    subway_id              VARCHAR(10) NOT NULL,
    station_id             VARCHAR(20) NOT NULL,     -- statnId
    station_name           VARCHAR(100),
    updn_line              SMALLINT NOT NULL,        -- updnLine 0/1
    train_line_nm          VARCHAR(100),             -- trainLineNm
    prev_station_id        VARCHAR(20),              -- statnFid
    next_station_id        VARCHAR(20),              -- statnTid
    transfer_count         SMALLINT NOT NULL DEFAULT 0,   -- trnsitCo
    ord_key                VARCHAR(20),              -- ordkey 원본
    ord_updn               CHAR(1),                  -- 파싱
    ord_seq                CHAR(1),                  -- 파싱 (첫번째/두번째)
    ord_remaining_stops    SMALLINT,                 -- 파싱
    ord_dest_code          VARCHAR(10),              -- 파싱
    ord_express            CHAR(1),                  -- 파싱
    transfer_line_ids      TEXT[],                   -- subwayList
    transfer_station_ids   TEXT[],                   -- statnList
    train_type             VARCHAR(20),              -- btrainSttus (급행, ITX)
    arrival_seconds        INT,                      -- barvlDt
    train_no               VARCHAR(20),              -- btrainNo
    final_station_id       VARCHAR(20),              -- bstatnId
    final_station_name     VARCHAR(100),             -- bstatnNm
    first_msg              VARCHAR(200),             -- arvlMsg2
    second_msg             VARCHAR(200),             -- arvlMsg3
    arrival_code           SMALLINT,                 -- arvlCd 0~5, 99
    is_last_car            BOOLEAN NOT NULL DEFAULT false,  -- lstcarAt
    raw_id                 UUID,                     -- FK → raw_public_data
    PRIMARY KEY (id, recptn_dt)
) PARTITION BY RANGE (recptn_dt);

-- 일 단위 파티션 (TimescaleDB 없이도 가능)
-- 상위 파티션 자동 생성 로직은 배치에서 처리
CREATE TABLE subway_realtime_arrivals_2026_10_20
  PARTITION OF subway_realtime_arrivals
  FOR VALUES FROM ('2026-10-20') TO ('2026-10-21');

CREATE INDEX idx_arrivals_station_time ON subway_realtime_arrivals (station_id, recptn_dt DESC);
CREATE INDEX idx_arrivals_subway_time  ON subway_realtime_arrivals (subway_id, recptn_dt DESC);
CREATE INDEX idx_arrivals_train_no     ON subway_realtime_arrivals (train_no, recptn_dt DESC);
CREATE INDEX idx_arrivals_code         ON subway_realtime_arrivals (arrival_code);
CREATE INDEX idx_arrivals_transfer_gin ON subway_realtime_arrivals
    USING gin (transfer_line_ids);