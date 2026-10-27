CREATE TABLE IF NOT EXISTS bus_realtime_arrivals (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fetched_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    city_code               VARCHAR(9) NOT NULL,
    node_id                 VARCHAR(30) NOT NULL,     -- nodeid
    node_name               VARCHAR(30),              -- nodenm
    route_id                VARCHAR(30) NOT NULL,     -- routeid
    route_no                VARCHAR(30),              -- routeno
    route_type              VARCHAR(10),              -- routetp
    arr_prev_station_cnt    SMALLINT,                 -- arrprevstationcnt
    vehicle_type            VARCHAR(10),              -- vehicletp
    arr_time_seconds        INT,                      -- arrtime (초)
    source                  VARCHAR(20) NOT NULL DEFAULT 'tago',
    service                 VARCHAR(80) NOT NULL DEFAULT 'getSttnAcctoArvlPrearngeInfoList',
    raw_id                  UUID,                     -- FK → raw_public_data
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_bus_arrivals_node_time
    ON bus_realtime_arrivals (city_code, node_id, fetched_at DESC);
CREATE INDEX IF NOT EXISTS idx_bus_arrivals_route_time
    ON bus_realtime_arrivals (route_id, fetched_at DESC);
