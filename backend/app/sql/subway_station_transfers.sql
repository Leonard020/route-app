CREATE TABLE subway_station_transfers (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    station_id          VARCHAR(20) NOT NULL,   -- statnId (기준역)
    transfer_subway_id  VARCHAR(10) NOT NULL,   -- subwayList 항목
    transfer_station_id VARCHAR(20) NOT NULL,   -- statnList 항목
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (station_id, transfer_station_id)
);

CREATE INDEX idx_transfers_station ON subway_station_transfers (station_id);