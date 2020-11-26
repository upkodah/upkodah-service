seoulbus.py
===========

공공 데이터 포털(data.go.kr)의 서울 버스 API를 사용하는 모듈입니다.

#### 목적
모듈 내 함수들을 이용하여 목적지에서 일정 시간이 걸리는 버스 정류소의 위치를 탐색하는 기능을 구현합니다.

## 모듈
> 1. get_station_by_pos
>
> 2. get_route_by_station
>
> 3. get_station_by_route

### read_key(key_name)

<pre>
<code>
    key = read_key(key_name)
</code>
</pre>
'config.ini' 에서 key 문자열을 읽어옵니다. 

key_name은 공공데이터포털은 'kr.go.data.'로 시작하고,
 카카오로컬의 경우 'kakaolocal.'과 같은 이름을 가집니다.

## 1. get_station_by_pos

<pre>
<code>
    ard_id_list = get_station_by_pos(gpsX, gpsY, radius=DFT_RADIUS)
</code>
</pre>
좌표(gpsX, gpsY), 탐색 반경을 입력하면 주변 정류소 id(ars_id) list를 반환합니다.

## 2. get_route_by_station

<pre>
<code>
    route_list = get_route_by_station(ars_id)
</code>
</pre>
   정류소 id(ars_id)를 입력받아 해당 정류소를 지나는 노선(route_list) 반환합니다.

## 3. get_station_by_route

<pre>
<code>
    ars_id_list = get_station_by_route(route)
</code>
</pre>
    버스 노선 ID(route)를 받아 '경유하는 정류소들의 목록(ars_id_list)' 반환합니다.

