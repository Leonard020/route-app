CREATE TABLE IF NOT EXISTS subway_realtime_arrivals (
    id                     UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    recptn_dt              TIMESTAMPTZ NOT NULL,
    fetched_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
    subway_id              VARCHAR(10) NOT NULL,
    station_id             VARCHAR(20) NOT NULL,
    station_name           VARCHAR(100),
    updn_line              SMALLINT NOT NULL,
    train_line_nm          VARCHAR(100),
    prev_station_id        VARCHAR(20),
    next_station_id        VARCHAR(20),
    transfer_count         SMALLINT NOT NULL DEFAULT 0,
    ord_key                VARCHAR(20),
    ord_updn               CHAR(1),
    ord_seq                CHAR(1),
    ord_remaining_stops    SMALLINT,
    ord_dest_code          VARCHAR(10),
    ord_express            CHAR(1),
    transfer_line_ids      TEXT[],
    transfer_station_ids   TEXT[],
    train_type             VARCHAR(20),
    arrival_seconds        INT,
    train_no               VARCHAR(20),
    final_station_id       VARCHAR(20),
    final_station_name     VARCHAR(100),
    first_msg              VARCHAR(200),
    second_msg             VARCHAR(200),
    arrival_code           SMALLINT,
    is_last_car            BOOLEAN NOT NULL DEFAULT false,
    raw_id                 UUID
);

CREATE INDEX IF NOT EXISTS idx_arrivals_station_time ON subway_realtime_arrivals (station_id, recptn_dt DESC);
CREATE INDEX IF NOT EXISTS idx_arrivals_subway_time  ON subway_realtime_arrivals (subway_id, recptn_dt DESC);
CREATE INDEX IF NOT EXISTS idx_arrivals_train_no     ON subway_realtime_arrivals (train_no, recptn_dt DESC);
CREATE INDEX IF NOT EXISTS idx_arrivals_code         ON subway_realtime_arrivals (arrival_code);
