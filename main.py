import destination_search
import SeoulBusAPI
import numpy as np

serviceKey = "SVpCy0bvZ5pGxpQdz6HmdUFgFl5L6vUbmK9tzQAPslFjjRHSBsKGTvYAkRC84aHoeUct2mtsiD8YfWyEzOQMIQ%3D%3D"


'''
1. 좌표, 시간 입력   ->   주변 버스 정류소 ID 반환
2. 정류소 ID 입력    ->   버스 노선 획득  
3. 획득한 버스 노선에서 출발지, 목적지 시간 계산하여 도착 버스 정류장 반환
'''


print("좌표 - 인접 정류소 ID 검색...")
bSt = SeoulBusAPI.BusStation(serviceKey)

gpsX = 127.0816985  # 동경 - 경도
gpsY = 37.5642135  # 북위 - 위도
time = 20

station_list = bSt.findStation(gpsX, gpsY)
print(station_list)  #근처 정류장 모두 찾기

print("정류소 - 경유 노선 검색...")
bus_route = []

for station in station_list:
    get_route = SeoulBusAPI.BusRoute(serviceKey).getRoute(station)
    for i in get_route:
        if i not in bus_route:
            bus_route.append(i)

print(bus_route)

for route in bus_route:

    df = destination_search.GetStationByBusRoute(route).search()
    station_num = list(np.array(df['정류소번호'].tolist()))
    bus_direction = list(np.array(df['진행방향'].tolist()))
    gps_x = list(np.array(df['gpsX'].tolist()))
    gps_y = list(np.array(df['gpsY'].tolist()))

    for station in station_list:
        if station in station_num:
            start_index = station_num.index(station)
            dest_index = start_index + int(time)

            if len(station_num)-1 < dest_index:
                break

            if bus_direction[start_index] == bus_direction[dest_index]:
                path = destination_search.PathData()
                req_time, stt = path.search(gps_x[start_index], gps_y[start_index], gps_x[dest_index], gps_y[dest_index], route)
                print('소요시간 : ' + req_time)
                print('도착 정류장 : ' + stt)
