import destination_search

'''
test용 값
gpsX = 127.0816985  # 동경 - 경도
gpsY = 37.5642135  # 북위 - 위도
time = 20


1. 좌표, 시간 입력   ->   주변 버스 정류소 ID 반환
2. 정류소 ID 입력    ->   버스 노선 획득  
3. 획득한 버스 노선에서 출발지, 목적지 시간 계산하여 도착 버스 정류장 반환
'''

print("gps_x : ", end='')
gps_x = input()
print("gps_y : ", end='')
gps_y = input()
print("time : ", end='')
time = int(input())

print('gps X : ', gps_x, 'gps Y : ', gps_y, 'time : ', time)

result = destination_search.DestinationStation(gps_x, gps_y, time)
print('gps_x, gps_y, 도착 시간, 도착 정류장')
result.show_result()
