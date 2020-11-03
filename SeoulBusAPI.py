from urllib.request import urlopen
from urllib.parse import unquote
from bs4 import BeautifulSoup

# URL - request format
API_STATION = "http://ws.bus.go.kr/api/rest/stationinfo/"       # BusStation, BusRoute
API_ROUTE = "http://ws.bus.go.kr/api/rest/busRouteInfo/"        # BusRouteNode

FUNC_ST_BY_POS = "/getStationByPos"
FUNC_RT_BY_ST = "/getRouteByStation"
FUNC_ND_BY_RT = "/getStaionByRoute"

# 서울특별시 경위도 한계
LONG_UPP = 127.269311       # 서울특별시 경도 상한 X
LONG_LOW = 126.734086       # 서울특별시 경도 하한
LATI_UPP = 37.715133        # 서울특별시 위도 상한 Y
LATI_LOW = 37.413294        # 서울특별시 위도 하한


# header code enum for checking
#headerCd = ("OK", )

class BusStation:           
    '''
    좌표 값을 입력받아 정류소 ID를 저장하는 클래스
    
    클래스 생성 후 findStation 메소드를 실행하여 결과를 얻는다.

    
    [Members] 

    (형식 멤버)  serviceKey  requestForm 

    (정보 멤버)  gpsX   gpsY    radius    numStop     itemList        arsIdList       arsIdStr

    [Methods]    findStation
    
    (CallBackURL: http://ws.bus.go.kr/api/rest/stationinfo/getStationByPos)
    '''

    def __init__(self, serviceKey):
        '''
        공공 데이터 포털에서 발급받은 Service Key를 입력받아 초기화

        gpsX, gpsY의 default 값은 서울의 중앙 좌표로 정의(을지로 주변)
        '''    
        # serviceKey와 request foramat 초기화
        self.serviceKey = unquote(serviceKey)
        self.requestForm = API_STATION + FUNC_ST_BY_POS + "?serviceKey=" + self.serviceKey    # request 형식 = CallBackURL + serviceKey
        
        self.numStop = 0

        # 요청 변수 없이 요청하여 API 검사
        xmlStation = urlopen(self.requestForm)
        bsStation = BeautifulSoup(xmlStation.read(), 'lxml-xml')
        
        # URL 응답이 있는지 검사
        headerCode = int(bsStation.find("headerCd").contents[0])

        ## URL 체크
        if headerCode == 0 or headerCode == 3:
            print(">>> 정상 작동")
            '''
        elif headerCode == 3:
            print(">>> 결과 없음")
            '''
        else:
            print(">>> API 요청 오류")
        ## URL 체크


    def findStation(self, gpsX, gpsY, radius=150):
        '''
        객체 생성 후 API 요청을 위해 실행하는 메소드. 해당 위치 주변의 정류소를 저장한다.
        정류소가 0개일 경우 검색 반경을 넓혀서 재요청한다.
        정류소 목록을 반환한다.
        
        [params]
        (param1) serviceKey:  서비스 키
        (param2) gpsX:        경도(126~127.xxxxxx)
        (param3) gpsY:        위도(37.xxxxxx)
        (param4) radius:      검색 반경(default-150m, 정류장이 없을 때 50씩 증가)
        
        [return]
        arsIdList:            정류소 목록
        '''
        # 초기화
        self.gpsX = gpsX
        self.gpsY = gpsY
        self.radius = radius
        

        while self.numStop == 0:
            request_Gps2Stop = self.requestForm + "&tmX=" + str(gpsX) + "&tmY=" + str(gpsY) + "&radius=" + str(radius)
           
            xmlStation= urlopen(request_Gps2Stop)  # 출력 XML 텍스트
            bsStation = BeautifulSoup(xmlStation.read(), 'lxml-xml')    # Parsing XML
            # 헤더 검사
            headerCode = int(bsStation.find("headerCd").contents[0])
            if headerCode == 5:
                print(">>> 잘못된 경위도 입력") # Error event: To Input Wrong GPS 
                return None
            elif headerCode == 3:
                self.numStop = 0
                self.radius = self.radius + 50
                continue

            self.itemList = bsStation.findAll('itemList')
            self.numStop = len(self.itemList)
            if self.numStop == 0:                   # 찾은 정류장이 없으면
                if self.radius <= 1500:
                    self.radius = self.radius + 50
                    continue
                else:
                    self.numStop = 0
                    return None

            self.arsIdList = list(range(0, self.numStop))
            for i in range(0, self.numStop):
                # input arsIdList
                self.arsIdList[i] = self.itemList[i].find('arsId').contents[0]
            return self.arsIdList
      

    def __str__(self):
        if self.numStop == 0:
            return "None"
        self.result_str = []
        for i in range(self.numStop):
            self.result_str.append(self.arsIdList[i])
        self.result_str = str(self.result_str)
        return self.result_str



class BusRoute:
    '''
    정류소 ID를 입력받아 해당 정류소를 지나는 노선을 저장하는 클래스

    - 객체 생성 후, findRoute를 통해 노선 저장.

    [Members]   

    (형식 멤버)  serviceKey  requestForm

    (정보 멤버)     arsId   numStop   itemList    busRouteIdList

    [Methods]    findRoute
    
    (CallBackURL: http://ws.bus.go.kr/api/rest/stationinfo/getRouteByStation)
    '''
    def __init__(self, serviceKey):
        '''
        공공 데이터 포털에서 발급받은 Service Key를 입력받아 초기화

        '''
        # 초기화
        self.serviceKey = unquote(serviceKey)
        self.requestForm = API_STATION + FUNC_RT_BY_ST + "?serviceKey=" + self.serviceKey
    
        # 요청 get raw data
        xmlStation = urlopen(self.requestForm)
        bsStation = BeautifulSoup(xmlStation.read(), 'lxml-xml')
        
        # URL 응답이 있는지 검사
        headerCode = int(bsStation.find("headerCd").contents[0])

        ## URL 체크
        if headerCode == 4 or headerCode == 0:
            print(">>> 정상 작동")
        else:
            print(">>> API 요청 오류")
        ## URL 체크


    def getRoute(self, arsId):
        '''
        하나의 정류소 ID를 받아 request.
        '''

        self.arsId = arsId
        request_Stop2Route = self.requestForm + "&arsId=" + arsId

        # 출력 XML 텍스트
        xmlRoute = urlopen(request_Stop2Route)

        # Parsing XML Busstop 
        bsRoute = BeautifulSoup(xmlRoute.read(), 'lxml-xml')

        self.itemList = bsRoute.findAll('itemList')
        self.numItem = len(self.itemList)

        busRouteIdList = list(range(self.numItem))
        for i in range(0,self.numItem):
            # input arsIdList
            busRouteIdList[i] = self.itemList[i].find('busRouteId').contents[0]
        return busRouteIdList

    def findRoute(self, stationList):
        '''
         정류소의 List를 입력받아 처리 for문으로 구성
        '''
        if stationList == None:
            return None
        # 입력 정류소 길이
        self.numStation = len(stationList)

        '''
         정류소ID와 연관된 노선 ID 목록을 입력하고자 해서 튜플로 이루어진 리스트를 만든다.

         아래와 같이 만들고 나니 바로 출력할 수 없어 출력 함수를 만든다.
        '''

        self.Station_Route = list()     # 튜플들을 넣을 빈 리스트 생성

        for i in range(0, self.numStation):
            busRouteIdList = self.getRoute(stationList[i])
            self.Station_Route.append((stationList[i], busRouteIdList))    # (정류소 ID, 지나는 노선) 튜플들의 리스트

        return self.Station_Route

    # 목록 중 하나를 출력하느 메소드
    def showRoute(self, stationId = '00000', indexStation = 0):
        if stationId != '00000':          # stationID 입력이 있을 경우 -> 리스트 검사
            counter = 0
            for (arsId, busRouteIdList) in self.Station_Route:
                if arsId == stationId:
                    print("정류소 ID: " + stationId)
                    print("지나는 노선 ID:", end = ' ')
                    print(busRouteIdList)
                    counter += 1
                    return 1
            if counter == 0:
                print(">>> 일치하는 정류소 ID 없음")
                return 0

        elif indexStation < self.numStation:
            print("정류소 ID: " + self.Station_Route[0][indexStation])
            print("지나는 노선 ID: ", end = ' ')
            print(self.Station_Route[1][indexStation])
    
    # 전체 목록을 출력하는 메소드
    def showAll(self):
        if self.numStation == 0:            # 에러
            print("원하는 결과를 출력할 수 없음")
            return None
        
        print("총 정류소 개수: ", self.numStation)
        i=0
        for (arsId, busRouteIdList) in self.Station_Route:
            print("<",i,">")
            print("정류소 ID: " + arsId)
            print("노선 목록: ", end = ' ')
            print(busRouteIdList)
            i = i+1
        return self.numStation * self.itemList

    def __str__(self):
        self.result_str = []      # 결과 문자열 생성    - list로 생성됨.
        for (arsId, busRouteIdList) in self.Station_Route:
            # 문자열
            self.result_str.append(str(arsId))
            self.result_str.append(busRouteIdList)
        self.result_str = str(self.result_str)      # list 객체를 문자열로 변환

        return self.result_str
        
   

class BusNode:
    '''
    버스 노선 ID를 받아 버스 경유 노선 목록을 저장하는 클래스

    - 객체 생성 후, findRouteNode로 실행하여 노선 목록 생성

    [Member]

    (형식 멤버)  serviceKey  requestForm

    (정보 멤버)  busRouteId    numItem   itemList    busStationIdList

    [Method]    findRouteNode(self, busRouteId)

    (CallBack URL: http://ws.bus.go.kr/api/rest/busRouteInfo/getStaionByRoute)

    '''
    

    def __init__(self, serviceKey):
        '''
        공공 데이터 포털에서 발급받은 Service Key를 입력받아 초기
        '''
        #초기화
        self.serviceKey = unquote(serviceKey)
        self.requestForm = API_ROUTE + FUNC_ND_BY_RT + "?serviceKey=" + serviceKey

        xmlNode = urlopen(self.requestForm)
        bsNode = BeautifulSoup(xmlNode.read(), 'lxml-xml')

        # URL 응답이 있는지 검사
        headerCode = int(bsNode.find("headerCd").contents[0])

        ## URL 체크
        if headerCode == 4 or headerCode == 0:      # 요청 busRouteId가 없어 검색결과 없음(4)
            print(">>> 정상 작동")
        else:
            print(">>> API 요청 오류(code:", headerCode, ")")
    
    def getNode(self, busRouteId):
        '''
            (단위 요청 메소드) API call 실행
            버스 노선 ID 하나를 주고 해당 노선의 경유 정류소 목록을 반환하는 메소드
        '''
        # 입력 버스노선정보 저장
        self.busRouteId = busRouteId
        
        # API 요청 및 파싱
        requestNode = self.requestForm + "&busRouteId=" + busRouteId 
        xmlNode = urlopen(requestNode)
        bsNode = BeautifulSoup(xmlNode.read(), 'lxml-xml')

        self.itemList = bsNode.findAll('itemList')
        self.numItem = len(self.itemList)

        self.busNodeList = list(range(self.numItem))
        for i in range(0, self.numItem):
            # input arsIdList
            self.busNodeList[i] = self.itemList[i].find('arsId').contents[0]
        return self.busNodeList

    def getListNode(self, busRouteIdList):
        '''
        getNode 메소드를 사용하여 노선 List의 결과를 반환
        '''
        Route_Node = list()
        for busRouteId in busRouteIdList:
            nodeList = self.getNode(busRouteId)
            Route_Node.append((busRouteId, nodeList)) # 노선ID와 노드 리스트를 튜플 연관
        return Route_Node


    def findNode(self, Station_Route, numStation):       # 정류소 ID를 포함하는 튜플(Station_Route)을 입력 받음.
        '''
            이전 클래스(busRoute)의 결과를 받아 요청 결과를 출력하는 메소드
        '''
        if Station_Route == None:      # invalid input error
            return None
        # parsing  tuple List
        #self.numStation = len(Station_Route)       # 정류소 숫자       len하면 에러 발생
        self.numStation = numStation
        self.resultList = list()                 # 결과 정보 리스트 (정류소, 노선, 경유 목록, 인덱스)튜플 리스트
        for (stationId, busRouteIdList) in Station_Route:   #   Station_Route 튜플 리스트에 대한 for문

            for busRouteId in busRouteIdList:
                busNodeList = self.getNode(busRouteId)         # 정류소 목록
                # 목록 중 index 찾기
                nodeIndex = 0
                for NodeId in busNodeList:
                    if NodeId == stationId:
                        break
                    nodeIndex = nodeIndex + 1
                
                self.resultList.append((stationId, busRouteId, nodeIndex, busNodeList))

        return self.resultList
    
    
    def showResult(self):
        if self.numStation == 0:
            print("원하는 결과를 출력할 수 없음")
        #
        for (stationId, busRouteId, nodeIndex, busNodeList) in self.resultList:
            print("Station ID: " + stationId + ", Route ID: " + busRouteId + ", Index: " + str(nodeIndex))
        


        
        
'''
API 사용 클래스 테스트 코드
'''
if __name__ == "__main__":
   serviceKey = "SVpCy0bvZ5pGxpQdz6HmdUFgFl5L6vUbmK9tzQAPslFjjRHSBsKGTvYAkRC84aHoeUct2mtsiD8YfWyEzOQMIQ%3D%3D"

   print("좌표 - 인접 정류소 ID 검색...")
   bSt = BusStation(serviceKey)

   gpsX = 127.0816985                # 동경 - 경도
   gpsY = 37.5642135                # 북위 - 위도
   
   stationList = bSt.findStation(gpsX, gpsY)
   print(bSt)
   
   print("정류소 - 경유 노선 검색...")
   bRt = BusRoute(serviceKey)
   routeList = bRt.findRoute(stationList)
   bRt.showRoute('05115')
   bRt.showAll()
   if routeList == None:
       print("결과없음")
   else:
       #br.showAll()
       print(bRt)

   bNd = BusNode(serviceKey)
   nodeList = bNd.findNode(bRt.Station_Route, bRt.numStation)
   #print("test route node: " + nodeList)
   bNd.showResult()