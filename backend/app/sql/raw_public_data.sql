CREATE TABLE raw_public_data (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source          VARCHAR(50)  NOT NULL,   -- 'seoul_subway'
    service         VARCHAR(100) NOT NULL,   -- 'realtimeStationArrival/ALL'
    request_url     TEXT,
    request_params  JSONB,
    http_status     SMALLINT,
    content_type    VARCHAR(50),
    body            TEXT,                    -- 원본 XML/JSON 그대로
    result_code     VARCHAR(20),             -- INFO-000 / ERROR-300 ...
    result_message  VARCHAR(500),
    record_count    INT,
    fetched_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    parsed_at       TIMESTAMPTZ,
    parse_error     TEXT
);

CREATE INDEX idx_raw_source_fetched ON raw_public_data (source, fetched_at DESC);
CREATE INDEX idx_raw_result_code    ON raw_public_data (result_code);