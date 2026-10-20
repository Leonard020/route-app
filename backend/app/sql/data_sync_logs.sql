CREATE TABLE data_sync_logs (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source          VARCHAR(50)  NOT NULL,
    service         VARCHAR(100) NOT NULL,
    started_at      TIMESTAMPTZ NOT NULL,
    finished_at     TIMESTAMPTZ,
    status          VARCHAR(20) NOT NULL,    -- success/partial/failed
    items_fetched   INT DEFAULT 0,
    items_saved     INT DEFAULT 0,
    items_failed    INT DEFAULT 0,
    error_code      VARCHAR(20),
    error_message   TEXT
);

CREATE INDEX idx_sync_source_started ON data_sync_logs (source, started_at DESC);