CREATE TABLE IF NOT EXISTS raw_public_data (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source          VARCHAR(50)  NOT NULL,
    service         VARCHAR(100) NOT NULL,
    request_url     TEXT,
    request_params  JSONB,
    http_status     SMALLINT,
    content_type    VARCHAR(50),
    body            TEXT,
    result_code     VARCHAR(20),
    result_message  VARCHAR(500),
    record_count    INT,
    fetched_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    parsed_at       TIMESTAMPTZ,
    parse_error     TEXT
);
CREATE INDEX IF NOT EXISTS idx_raw_source_fetched ON raw_public_data (source, fetched_at DESC);
CREATE INDEX IF NOT EXISTS idx_raw_result_code    ON raw_public_data (result_code);

CREATE TABLE IF NOT EXISTS data_sync_logs (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source          VARCHAR(50)  NOT NULL,
    service         VARCHAR(100) NOT NULL,
    started_at      TIMESTAMPTZ NOT NULL,
    finished_at     TIMESTAMPTZ,
    status          VARCHAR(20) NOT NULL,
    items_fetched   INT DEFAULT 0,
    items_saved     INT DEFAULT 0,
    items_failed    INT DEFAULT 0,
    error_code      VARCHAR(20),
    error_message   TEXT
);
CREATE INDEX IF NOT EXISTS idx_sync_source_started ON data_sync_logs (source, started_at DESC);

CREATE TABLE IF NOT EXISTS subway_api_error_codes (
    code        VARCHAR(20) PRIMARY KEY,
    level       VARCHAR(10) NOT NULL,
    message     VARCHAR(500) NOT NULL,
    retryable   BOOLEAN NOT NULL DEFAULT false,
    description TEXT
);
INSERT INTO subway_api_error_codes (code, level, message, retryable, description) VALUES
 ('INFO-000',  'INFO',  '정상 처리되었습니다',                     false, NULL),
 ('INFO-100',  'INFO',  '인증키가 유효하지 않습니다',                false, '키 확인 필요'),
 ('INFO-200',  'INFO',  '해당하는 데이터가 없습니다',                 false, '빈 응답'),
 ('ERROR-300', 'ERROR', '필수 값이 누락되어 있습니다',                false, '파라미터 확인'),
 ('ERROR-301', 'ERROR', '파일타입 값이 누락 혹은 유효하지 않습니다',   false, 'TYPE 파라미터'),
 ('ERROR-310', 'ERROR', '해당하는 서비스를 찾을 수 없습니다',         false, 'SERVICE 파라미터'),
 ('ERROR-331', 'ERROR', '요청시작위치 값을 확인하십시오',             false, 'START_INDEX'),
 ('ERROR-332', 'ERROR', '요청종료위치 값을 확인하십시오',             false, 'END_INDEX'),
 ('ERROR-333', 'ERROR', '요청위치 값의 타입이 유효하지 않습니다',     false, NULL),
 ('ERROR-334', 'ERROR', '요청종료위치 보다 요청시작위치가 더 큽니다',  false, NULL),
 ('ERROR-335', 'ERROR', '샘플데이터는 한번에 최대 5건',              false, '샘플키 제약'),
 ('ERROR-336', 'ERROR', '데이터요청은 한번에 최대 1000건',           true,  '페이지 분할 필요'),
 ('ERROR-500', 'ERROR', '서버 오류입니다',                          true,  NULL),
 ('ERROR-600', 'ERROR', '데이터베이스 연결 오류입니다',              true,  NULL),
 ('ERROR-601', 'ERROR', 'SQL 문장 오류 입니다',                     true,  NULL)
ON CONFLICT (code) DO NOTHING;

CREATE TABLE IF NOT EXISTS bus_api_error_codes (
    code           VARCHAR(20) PRIMARY KEY,
    source         VARCHAR(20) NOT NULL,
    message        VARCHAR(200) NOT NULL,
    description    TEXT
);
INSERT INTO bus_api_error_codes (code, source, message, description) VALUES
 ('1',  'portal', 'APPLICATION_ERROR', '어플리케이션 에러'),
 ('4',  'portal', 'HTTP_ERROR', 'HTTP에러'),
 ('12', 'portal', 'NO_OPENAPI_SERVICE_ERROR', '해당 오픈API서비스가 없거나 폐기됨'),
 ('20', 'portal', 'SERVICE_ACCESS_DENIED_ERROR', '서비스 접근거부'),
 ('22', 'portal', 'LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR', '서비스 요청제한횟수 초과에러'),
 ('30', 'portal', 'SERVICE_KEY_IS_NOT_REGISTERED_ERROR', '등록되지 않은 서비스키'),
 ('31', 'portal', 'DEADLINE_HAS_EXPIRED_ERROR', '활용기간 만료'),
 ('32', 'portal', 'UNREGISTERED_IP_ERROR', '등록되지 않은 IP'),
 ('99', 'portal', 'UNKNOWN_ERROR', '기타에러'),
 ('99P','provider','INVALID_REQUEST_PARAMETER_ERROR', '잘못된 요청 파라메터 에러')
ON CONFLICT (code) DO NOTHING;

CREATE TABLE IF NOT EXISTS subway_lines (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subway_id      VARCHAR(10) NOT NULL UNIQUE,
    line_name      VARCHAR(50) NOT NULL,
    line_type      VARCHAR(20),
    operator       VARCHAR(100),
    color          VARCHAR(10),
    display_order  INT,
    is_active      BOOLEAN NOT NULL DEFAULT true,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_subway_lines_display ON subway_lines (display_order);
INSERT INTO subway_lines (subway_id, line_name, display_order) VALUES
 ('1001','1호선',1),('1002','2호선',2),('1003','3호선',3),
 ('1004','4호선',4),('1005','5호선',5),('1006','6호선',6),
 ('1007','7호선',7),('1008','8호선',8),('1009','9호선',9),
 ('1061','중앙선',10),('1063','경의중앙선',11),('1065','공항철도',12),
 ('1067','경춘선',13),('1075','수인분당선',14),('1077','신분당선',15),
 ('1092','우이신설선',16),('1032','GTX-A',17)
ON CONFLICT (subway_id) DO NOTHING;

CREATE TABLE IF NOT EXISTS subway_stations (
    id                     UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    station_id             VARCHAR(20) NOT NULL UNIQUE,
    subway_id              VARCHAR(10) NOT NULL,
    line_name              VARCHAR(50),
    station_code           VARCHAR(10),
    station_name           VARCHAR(100) NOT NULL,
    station_name_norm      VARCHAR(100),
    prev_station_id        VARCHAR(20),
    next_station_id        VARCHAR(20),
    transfer_count         INT NOT NULL DEFAULT 0,
    is_transfer            BOOLEAN NOT NULL DEFAULT false,
    lat                    DOUBLE PRECISION,
    lng                    DOUBLE PRECISION,
    location               GEOGRAPHY(POINT, 4326),
    place_id               UUID,
    display_order          INT,
    is_active              BOOLEAN NOT NULL DEFAULT true,
    created_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at             TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_stations_subway ON subway_stations (subway_id, display_order);
CREATE INDEX IF NOT EXISTS idx_stations_name_trgm ON subway_stations USING gin (station_name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_stations_location ON subway_stations USING gist (location);
CREATE INDEX IF NOT EXISTS idx_stations_place ON subway_stations (place_id);

CREATE TABLE IF NOT EXISTS subway_station_transfers (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    station_id          VARCHAR(20) NOT NULL,
    transfer_subway_id  VARCHAR(10) NOT NULL,
    transfer_station_id VARCHAR(20) NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (station_id, transfer_station_id)
);
CREATE INDEX IF NOT EXISTS idx_transfers_station ON subway_station_transfers (station_id);

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
    raw_id                 UUID REFERENCES raw_public_data(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_arrivals_station_time ON subway_realtime_arrivals (station_id, recptn_dt DESC);
CREATE INDEX IF NOT EXISTS idx_arrivals_subway_time  ON subway_realtime_arrivals (subway_id, recptn_dt DESC);
CREATE INDEX IF NOT EXISTS idx_arrivals_train_no     ON subway_realtime_arrivals (train_no, recptn_dt DESC);
CREATE INDEX IF NOT EXISTS idx_arrivals_code         ON subway_realtime_arrivals (arrival_code);

CREATE TABLE IF NOT EXISTS bus_city_codes (
    city_code      VARCHAR(9) PRIMARY KEY,
    city_name      VARCHAR(100) NOT NULL,
    fetched_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_bus_city_name ON bus_city_codes (city_name);

CREATE TABLE IF NOT EXISTS bus_realtime_arrivals (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fetched_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    city_code               VARCHAR(9) NOT NULL,
    node_id                 VARCHAR(30) NOT NULL,
    node_name               VARCHAR(30),
    route_id                VARCHAR(30) NOT NULL,
    route_no                VARCHAR(30),
    route_type              VARCHAR(10),
    arr_prev_station_cnt    SMALLINT,
    vehicle_type            VARCHAR(10),
    arr_time_seconds        INT,
    source                  VARCHAR(20) NOT NULL DEFAULT 'tago',
    service                 VARCHAR(80) NOT NULL DEFAULT 'getSttnAcctoArvlPrearngeInfoList',
    raw_id                  UUID REFERENCES raw_public_data(id) ON DELETE SET NULL,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_bus_arrivals_node_time
    ON bus_realtime_arrivals (city_code, node_id, fetched_at DESC);
CREATE INDEX IF NOT EXISTS idx_bus_arrivals_route_time
    ON bus_realtime_arrivals (route_id, fetched_at DESC);
