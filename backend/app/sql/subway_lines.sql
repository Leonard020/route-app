CREATE TABLE subway_lines (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subway_id      VARCHAR(10) NOT NULL UNIQUE,   -- '1001','1002',...,'1032'
    line_name      VARCHAR(50) NOT NULL,          -- '1호선','GTX-A'
    line_type      VARCHAR(20),                   -- 일반/급행/광역
    operator       VARCHAR(100),
    color          VARCHAR(10),
    display_order  INT,
    is_active      BOOLEAN NOT NULL DEFAULT true,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_subway_lines_display ON subway_lines (display_order);

-- 명세서의 17개 노선 시드
INSERT INTO subway_lines (subway_id, line_name, display_order) VALUES
 ('1001','1호선',1),('1002','2호선',2),('1003','3호선',3),
 ('1004','4호선',4),('1005','5호선',5),('1006','6호선',6),
 ('1007','7호선',7),('1008','8호선',8),('1009','9호선',9),
 ('1061','중앙선',10),('1063','경의중앙선',11),('1065','공항철도',12),
 ('1067','경춘선',13),('1075','수인분당선',14),('1077','신분당선',15),
 ('1092','우이신설선',16),('1032','GTX-A',17);