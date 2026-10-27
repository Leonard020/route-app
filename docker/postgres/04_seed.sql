INSERT INTO places (name, address, category, lat, lng, location, external_id, raw)
VALUES
 ('강남역', '서울 강남구 강남대로 396', 'subway', 37.4979, 127.0276,
  ST_SetSRID(ST_MakePoint(127.0276, 37.4979), 4326)::geography,
  '1002000222',
  '{"subway_id":"1002","station_id":"1002000222","station_name":"강남"}'::jsonb),
 ('서울역', '서울 중구 한강대로 405', 'subway', 37.5547, 126.9707,
  ST_SetSRID(ST_MakePoint(126.9707, 37.5547), 4326)::geography,
  '1001000100',
  '{"subway_id":"1001","station_id":"1001000100","station_name":"서울"}'::jsonb),
 ('시청역', '서울 중구 세종대로 110', 'subway', 37.5651, 126.9770,
  ST_SetSRID(ST_MakePoint(126.9770, 37.5651), 4326)::geography,
  '1001000132',
  '{"subway_id":"1001","station_id":"1001000132","station_name":"시청"}'::jsonb),
 ('강남역.강남역버스환승센터', '서울 강남구 강남대로 396', 'bus', 37.4982, 127.0278,
  ST_SetSRID(ST_MakePoint(127.0278, 37.4982), 4326)::geography,
  'GGB204000376',
  '{"city_code":"11","node_id":"GGB204000376"}'::jsonb),
 ('서울역버스환승센터', '서울 중구 한강대로 405', 'bus', 37.5551, 126.9710,
  ST_SetSRID(ST_MakePoint(126.9710, 37.5551), 4326)::geography,
  'GGB115000001',
  '{"city_code":"11","node_id":"GGB115000001"}'::jsonb)
;

INSERT INTO subway_stations (station_id, subway_id, line_name, station_name, station_name_norm, lat, lng)
VALUES
 ('1002000222','1002','2호선','강남','강남',37.4979,127.0276),
 ('1001000100','1001','1호선','서울','서울',37.5547,126.9707),
 ('1001000132','1001','1호선','시청','시청',37.5651,126.9770)
ON CONFLICT (station_id) DO NOTHING;
