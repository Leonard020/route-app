CREATE TABLE IF NOT EXISTS guidance_sessions (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id                 UUID REFERENCES users(id) ON DELETE SET NULL,
    route_id                UUID NOT NULL REFERENCES routes(id) ON DELETE CASCADE,
    status                  VARCHAR(20) NOT NULL DEFAULT 'active',
    current_lat             DOUBLE PRECISION,
    current_lng             DOUBLE PRECISION,
    current_step_order      INT NOT NULL DEFAULT 1,
    remaining_duration_s    INT NOT NULL DEFAULT 0,
    off_route               BOOLEAN NOT NULL DEFAULT false,
    transfer_risk           BOOLEAN NOT NULL DEFAULT false,
    started_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    ended_at                TIMESTAMPTZ,
    CONSTRAINT guidance_status CHECK (status IN ('active','ended','off_route'))
);
CREATE INDEX IF NOT EXISTS idx_guidance_route ON guidance_sessions (route_id);
CREATE INDEX IF NOT EXISTS idx_guidance_user ON guidance_sessions (user_id, status);
