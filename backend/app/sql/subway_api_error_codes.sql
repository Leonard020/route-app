CREATE TABLE subway_api_error_codes (
    code        VARCHAR(20) PRIMARY KEY,
    level       VARCHAR(10) NOT NULL,        -- INFO / ERROR
    message     VARCHAR(500) NOT NULL,
    retryable   BOOLEAN NOT NULL DEFAULT false,
    description TEXT
);

-- 명세서의 15개 코드 전부 시드
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
 ('ERROR-601', 'ERROR', 'SQL 문장 오류 입니다',                     true,  NULL);