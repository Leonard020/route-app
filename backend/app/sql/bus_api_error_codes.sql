CREATE TABLE IF NOT EXISTS bus_api_error_codes (
    code           VARCHAR(20) PRIMARY KEY,
    source         VARCHAR(20) NOT NULL,       -- portal / provider
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
