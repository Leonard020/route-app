CREATE TABLE IF NOT EXISTS users (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email           VARCHAR(255) UNIQUE,
    phone           VARCHAR(20) UNIQUE,
    password_hash   VARCHAR(255),
    provider        VARCHAR(20) NOT NULL DEFAULT 'local',
    provider_id     VARCHAR(255),
    nickname        VARCHAR(50) NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'active',
    role            VARCHAR(20) NOT NULL DEFAULT 'user',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at      TIMESTAMPTZ,
    CONSTRAINT users_status CHECK (status IN ('active','inactive','deleted')),
    CONSTRAINT users_role CHECK (role IN ('user','admin'))
);

CREATE TABLE IF NOT EXISTS user_preferences (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id                 UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    preferred_mode          VARCHAR(20) NOT NULL DEFAULT 'transit',
    avoid_highway           BOOLEAN NOT NULL DEFAULT false,
    avoid_toll              BOOLEAN NOT NULL DEFAULT false,
    accessibility           BOOLEAN NOT NULL DEFAULT false,
    eco_priority            BOOLEAN NOT NULL DEFAULT false,
    max_walk_min            INT NOT NULL DEFAULT 20,
    notify_enabled          BOOLEAN NOT NULL DEFAULT true,
    walk_speed              VARCHAR(20) NOT NULL DEFAULT 'normal',
    route_sort              VARCHAR(20) NOT NULL DEFAULT 'fastest',
    alert_alight            BOOLEAN NOT NULL DEFAULT true,
    alert_transfer          BOOLEAN NOT NULL DEFAULT true,
    alert_minutes_before    INT NOT NULL DEFAULT 3,
    dnd_start               TIME,
    dnd_end                 TIME,
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT pref_mode CHECK (preferred_mode IN ('walk','car','transit','bike','multi')),
    CONSTRAINT pref_walk_speed CHECK (walk_speed IN ('slow','normal','fast')),
    CONSTRAINT pref_route_sort CHECK (route_sort IN ('fastest','min_transfer','min_walk'))
);

CREATE TABLE IF NOT EXISTS places (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    external_id     VARCHAR(100),
    name            VARCHAR(255) NOT NULL,
    address         TEXT NOT NULL,
    road_address    TEXT,
    category        VARCHAR(50),
    lat             DOUBLE PRECISION NOT NULL,
    lng             DOUBLE PRECISION NOT NULL,
    location        GEOGRAPHY(POINT, 4326),
    phone           VARCHAR(30),
    opening_hours   JSONB,
    rating          NUMERIC(3, 2),
    raw             JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_places_external_id ON places (external_id);
CREATE INDEX IF NOT EXISTS idx_places_name_trgm ON places USING gin (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_places_location ON places USING gist (location);

CREATE TABLE IF NOT EXISTS favorites (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    place_id    UUID NOT NULL REFERENCES places(id) ON DELETE CASCADE,
    label       VARCHAR(50),
    sort_order  INT NOT NULL DEFAULT 0,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (user_id, place_id)
);

CREATE TABLE IF NOT EXISTS recent_searches (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID REFERENCES users(id) ON DELETE CASCADE,
    place_id    UUID REFERENCES places(id) ON DELETE SET NULL,
    keyword     VARCHAR(255),
    lat         DOUBLE PRECISION,
    lng         DOUBLE PRECISION,
    searched_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_recent_user_time ON recent_searches (user_id, searched_at DESC);

CREATE TABLE IF NOT EXISTS routes (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id                 UUID REFERENCES users(id) ON DELETE SET NULL,
    origin_place_id         UUID REFERENCES places(id) ON DELETE SET NULL,
    dest_place_id           UUID REFERENCES places(id) ON DELETE SET NULL,
    origin_lat              DOUBLE PRECISION NOT NULL,
    origin_lng              DOUBLE PRECISION NOT NULL,
    dest_lat                DOUBLE PRECISION NOT NULL,
    dest_lng                DOUBLE PRECISION NOT NULL,
    mode                    VARCHAR(20) NOT NULL,
    preference_snapshot     JSONB,
    total_distance_m        INT NOT NULL,
    total_duration_s        INT NOT NULL,
    total_cost              INT NOT NULL DEFAULT 0,
    transfer_count          INT NOT NULL DEFAULT 0,
    walk_distance_m         INT NOT NULL DEFAULT 0,
    carbon_g                INT NOT NULL DEFAULT 0,
    eta                     TIMESTAMPTZ,
    polyline                TEXT,
    status                  VARCHAR(20) NOT NULL DEFAULT 'active',
    predictor_version       VARCHAR(30),
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT routes_mode CHECK (mode IN ('walk','car','transit','bike','multi')),
    CONSTRAINT routes_status CHECK (status IN ('active','expired','rerouted'))
);

CREATE TABLE IF NOT EXISTS route_steps (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    route_id        UUID NOT NULL REFERENCES routes(id) ON DELETE CASCADE,
    step_order      INT NOT NULL,
    mode            VARCHAR(20) NOT NULL,
    instruction     TEXT,
    distance_m      INT NOT NULL,
    duration_s      INT NOT NULL,
    start_lat       DOUBLE PRECISION NOT NULL,
    start_lng       DOUBLE PRECISION NOT NULL,
    end_lat         DOUBLE PRECISION NOT NULL,
    end_lng         DOUBLE PRECISION NOT NULL,
    polyline        TEXT,
    transit_info    JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (route_id, step_order)
);

CREATE TABLE IF NOT EXISTS step_segments (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    step_id         UUID NOT NULL REFERENCES route_steps(id) ON DELETE CASCADE,
    seg_order       INT NOT NULL,
    distance_m      INT NOT NULL,
    duration_s      INT NOT NULL,
    congestion      SMALLINT,
    road_type       VARCHAR(20),
    polyline        TEXT,
    UNIQUE (step_id, seg_order)
);

CREATE TABLE IF NOT EXISTS notifications (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type        VARCHAR(30) NOT NULL,
    title       VARCHAR(200) NOT NULL,
    body        TEXT,
    payload     JSONB,
    channel     VARCHAR(20) NOT NULL DEFAULT 'push',
    status      VARCHAR(20) NOT NULL DEFAULT 'pending',
    sent_at     TIMESTAMPTZ,
    read_at     TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT notifications_type CHECK (type IN ('reroute','eta_change','depart','arrive','notice','transfer','alight')),
    CONSTRAINT notifications_status CHECK (status IN ('pending','sent','failed'))
);

CREATE TABLE IF NOT EXISTS feedbacks (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID REFERENCES users(id) ON DELETE SET NULL,
    route_id    UUID REFERENCES routes(id) ON DELETE SET NULL,
    type        VARCHAR(20) NOT NULL,
    rating      SMALLINT,
    category    VARCHAR(30),
    comment     TEXT,
    status      VARCHAR(20) NOT NULL DEFAULT 'open',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT feedbacks_type CHECK (type IN ('rating','report')),
    CONSTRAINT feedbacks_status CHECK (status IN ('open','reviewed','resolved')),
    CONSTRAINT feedbacks_rating CHECK (rating IS NULL OR (rating BETWEEN 1 AND 5))
);

CREATE TABLE IF NOT EXISTS predictions (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    route_id            UUID REFERENCES routes(id) ON DELETE SET NULL,
    predictor_version   VARCHAR(30) NOT NULL,
    kind                VARCHAR(20) NOT NULL,
    request             JSONB NOT NULL,
    response            JSONB NOT NULL,
    actual              JSONB,
    latency_ms          INT,
    fallback_used       BOOLEAN NOT NULL DEFAULT false,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT predictions_kind CHECK (kind IN ('eta','congestion','ranking'))
);

CREATE TABLE IF NOT EXISTS api_keys (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name        VARCHAR(100) NOT NULL,
    key_hash    VARCHAR(255) NOT NULL UNIQUE,
    scopes      TEXT[],
    expires_at  TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
