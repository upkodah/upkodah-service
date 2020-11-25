# 매물을 찾는 메인 알고리즘
목적지에서 사용자로부터 입력된 시간에 갈 수 있는 매물들을 표시해주는 메인 알고리즘 부분입니다.

## 공공데이터 포털 서비스키

서비스키로 아래의 2가지가 사용됩니다.
```
my_api_key = unquote('bhQZulxZSz%2FeMsDseMe2DSccTVB%2BQPnxTxDp4SrK7HYRP%2BS0YDiBn93FLz0d%2FMFbyMPUqAvaMqrtW4e9%2FnHYhA%3D%3D')
service_key = "SVpCy0bvZ5pGxpQdz6HmdUFgFl5L6vUbmK9tzQAPslFjjRHSBsKGTvYAkRC84aHoeUct2mtsiD8YfWyEzOQMIQ%3D%3D"
```

## 1. 목적지 근처의 버스 정류장 찾기
https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15000759

목적지의 gps 좌표를 기반으로 근처의 버스 정류장의 gps를 반환하는 공공데이터 api를 사용합니다.

## 2. 버스 노선 데이터 받기
https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15000193

공공데이터 api를 호출하여 버스 노선 데이터 중 아래의 데이터를 데이터 프레임으로 저장합니다.
```
'진행방향', '순번', '구간ID', '정류소ID', '정류소번호', '정류장이름', 'gpsX', 'gpsY', '구간속도', '구간거리'
```

## 3. 두 버스 정류장 사이의 시간 구하기
https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15000414

목적지에서 가까운 버스 정류장과 목표로 하는 매물에 가까운 버스 정류장 사이의 이동 시간을 구하기 위해 공공데이터 포털의 대중교통환승경로 조회 서비스 api를 이용합니다.
환승을 고려하지 않고 가는 경우만을 생각하기 때문에 처음 탑승했던 버스 노선과 환승 횟수를 기준으로 필터링하여 원하는 목적지의 버스 정류장을 출력합니다.


## 4. 목적지에서 입력된 시간에 갈 수 있는 버스 정류장의 gps 반환
1번을 통해 목적지 근처 버스 정류장의 gps 값을 얻습니다.

1번과 2번을 통해 목적지 근처 버스 정류장의 버스 노선 데이터를 데이터 프레임으로 받습니다.

2번과 3번을 통해 목적지에서 입력된 시간에 갈 수 있는 버스 정류장의 gps를 반환합니다.
>여기에서 다음과 같은 사항을 고려합니다.
>버스 진행방향을 통해 버스가 회차하여 가고있는 곳을 지정하지 않았는지 확인합니다.
>버스 한 구간의 시간은 구간거리 / 구간속도로 구합니다.
>서울시에 국한되어 사용되는 api이기 때문에 제외시켜야하는 버스 노선이 존재합니다.
>
