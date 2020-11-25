# 매물을 찾는 메인 알고리즘
목적지에서 사용자로부터 입력된 시간에 갈 수 있는 매물들을 표시해주는 메인 알고리즘 부분입니다.

## 공공데이터 포털 서비스키

서비스키로 아래의 2가지가 사용됩니다.
```
my_api_key = unquote('bhQZulxZSz%2FeMsDseMe2DSccTVB%2BQPnxTxDp4SrK7HYRP%2BS0YDiBn93FLz0d%2FMFbyMPUqAvaMqrtW4e9%2FnHYhA%3D%3D')
service_key = "SVpCy0bvZ5pGxpQdz6HmdUFgFl5L6vUbmK9tzQAPslFjjRHSBsKGTvYAkRC84aHoeUct2mtsiD8YfWyEzOQMIQ%3D%3D"
```

## 버스 노선 데이터 받기
https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15000193

공공데이터 포털을 호출하여 버스 노선 데이터 중 아래의 데이터를 데이터 프레임으로 저장한다.
```
'진행방향', '순번', '구간ID', '정류소ID', '정류소번호', '정류장이름', 'gpsX', 'gpsY', '구간속도', '구간거리'
```


## 두 버스 정류장 사이의 시간 구하기
https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15000414

목적지에서 가까운 버스 정류장과 목표로 하는 매물에 가까운 버스 정류장 사이의 이동 시간을 구하기 위해 공공데이터 포털의 대중교통환승경로 조회 서비스를 이용한다.
