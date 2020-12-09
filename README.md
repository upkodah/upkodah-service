upkodah-service
=================

get location, find close bus stop or subway station, or other service functions else

대중 교통(버스/지하철)의 ETA 기반 목적지 탐색 알고리즘의 구현.

목적지(통학 통근 지점), 시간을 입력하여 해당 시간 동안 도착할 수 있는 위치를 반환합니다.

> seoulbus.py와 seoulsubway.py, station_search.py

## 1. 서울버스 API (seoulbus.py)

 서울 버스 Open API의 요청을 처리하는 메소드들과
 
 버스로 입력 시간동안 이동할 수 있는 정류소를 반환하는 메소드로 이루어져 있습니다.
 
 <pre>
 <code>
     result_df find_station_by_time(gps_x, gps_y, time)
 </code>
 </pre>
 
 목적지와 시간을 입력하면 도착할 수 있는 정류소의 정보를 담은 dataframe을 반환합니다.
 
 
## 2. 지하철 API (station_search.py, seoulsubway.py)

  서울 지하철 Open API의 요청과 지하철 이용 목적지 탐색 알고리즘이 구현되어 있습니다.

  서울 지역의 지하철 예상 구간 시간 정보를 통해 예상 도착시간을 찾을 수 있도록 구현하였습니다.

  /station_search.py
 <pre>
 <code>
     result_df find_station_by_eta(gps_x, gps_y, eta)
 </code>
 </pre>
 
 #### 출력 예시
 <pre>
 <code>
    >>> print(find_station_by_eta(127.0816985, 37.5642135, 20))
    
        idx lane    name time  cumulative           x          y
    0  239  7호선  뚝섬유원지역    2      11.725  127.066706  37.531551
    1  240  7호선     청담역    3      14.725  127.053925  37.519489
    2  241  7호선   강남구청역    2      16.725  127.041289  37.517188
    3  242  7호선     학동역    2      18.725  127.031619  37.514251
    4  226  7호선     하계역    1      19.725  127.067954  37.636568
    5  227  7호선     공릉역    2      18.725  127.072931  37.625768
    6  228  7호선   태릉입구역    2      16.725  127.074860  37.617365
    7  229  7호선     먹골역    2      14.725  127.077729  37.610788
    8  230  7호선     중화역    1      12.725  127.079308  37.602582
    9  231  7호선     상봉역    3      11.725  127.085671  37.595920
 </code>
 </pre>
 
