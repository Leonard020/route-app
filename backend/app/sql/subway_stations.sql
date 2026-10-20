CREATE TABLE subway_stations (
    id                     UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    station_id             VARCHAR(20) NOT NULL UNIQUE,   -- statnId
    subway_id              VARCHAR(10) NOT NULL,          -- 논리 FK
    line_name              VARCHAR(50),
    station_code           VARCHAR(10),                   -- statnId suffix
    station_name           VARCHAR(100) NOT NULL,         -- statnNm
    station_name_norm      VARCHAR(100),                  -- 검색 정규화
    prev_station_id        VARCHAR(20),                   -- statnFid (self-ref)
    next_station_id        VARCHAR(20),                   -- statnTid (self-ref)
    transfer_count         INT NOT NULL DEFAULT 0,        -- trnsitCo
    is_transfer            BOOLEAN NOT NULL DEFAULT false,
    lat                    DOUBLE PRECISION,
    lng                    DOUBLE PRECISION,
    location               GEOGRAPHY(POINT, 4326),
    place_id               UUID,                          -- FK → places
    display_order          INT,
    is_active              BOOLEAN NOT NULL DEFAULT true,
    created_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at             TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_stations_subway        ON subway_stations (subway_id, display_order);
CREATE INDEX idx_stations_name_trgm     ON subway_stations
    USING gin (station_name gin_trgm_ops);
CREATE INDEX idx_stations_location      ON subway_stations USING gist (location);
CREATE INDEX idx_stations_place         ON subway_stations (place_id);