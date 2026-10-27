INSERT INTO places (name, address, category, lat, lng, location)
VALUES
 ('강남역', '서울 강남구 강남대로 396', 'subway', 37.4979, 127.0276, ST_SetSRID(ST_MakePoint(127.0276, 37.4979), 4326)::geography),
 ('서울역', '서울 중구 한강대로 405', 'subway', 37.5547, 126.9707, ST_SetSRID(ST_MakePoint(126.9707, 37.5547), 4326)::geography),
 ('시청역', '서울 중구 세종대로 110', 'subway', 37.5651, 126.9770, ST_SetSRID(ST_MakePoint(126.9770, 37.5651), 4326)::geography),
 ('강남역.강남역버스환승센터', '서울 강남구 강남대로 396', 'bus', 37.4982, 127.0278, ST_SetSRID(ST_MakePoint(127.0278, 37.4982), 4326)::geography),
 ('서울역버스환승센터', '서울 중구 한강대로 405', 'bus', 37.5551, 126.9710, ST_SetSRID(ST_MakePoint(126.9710, 37.5551), 4326)::geography)
;
