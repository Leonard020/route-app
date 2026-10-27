CREATE TABLE IF NOT EXISTS bus_city_codes (
    city_code      VARCHAR(9) PRIMARY KEY,     -- citycode
    city_name      VARCHAR(100) NOT NULL,      -- cityname
    fetched_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_bus_city_name ON bus_city_codes (city_name);
