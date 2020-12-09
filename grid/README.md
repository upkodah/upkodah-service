Grid System
===========

GeoGrid 클래스는 지리 좌표를 grid ID로 변환하기 위해 사용합니다.

GeoGrid는 생성될 때, 한국의 최극단(동,서,남,북)값과 기준 좌표(default: 서울시립대 좌표), 그리고 그리드 크기를 파라미터로 받아 초기화합니다.

위의 파라미터들의 디폴트 값들은 모두 geoconst.py에 선언되어 있습니다.

> 이 모듈에서는 그리드 기준 점을 통해 초기화하고,
>
> 이에 따른 grid ID를 얻는, 단순한 기능을 지원합니다. (get_grid_id)
>
> 또한, grid ID에서 grid의 중심 좌표를 얻을 수 있습니다. (grid_center)   
  

사용 예
----------
### 1  객체 생성

위에서 언급했던 것처럼 기준 좌표들과 그리드의 단위 크기를 설정할 수 있습니다.

모든 파라미터에는 디폴트 값(geoconst.py 참고)이 설정되어 있습니다.

<pre>
<code>
 gridsys = GeoGrid()        # 디폴트 객체 생성
</code>
</pre>

<pre>
<code>
 gridsys = GeoGrid(lon_std=SEOUL_MID_LON, lat_std=SEOUL_MID_LAT)        # 기준 좌표 변경 생성
</code>
</pre>

### 2  Grid ID 얻기
#### get_grid_id() 메소드
<pre>
<code>
 def get_grid_id(self, lon, lat):
  ...
 return literal_grid(grid_lon, grid_lat)
</code>
</pre>

#### 사용

float 형태의 좌표 x, y를 전달해주면 string 형태의 grid ID를 반환합니다.

<pre>
<code>
 grid_id = gridsys.get_grid_id(127.100637, 37.072855)
 print(f"grid ID: {grid_id}")
 
 >>> grid ID: 13750811
</code>
</pre>

### 3   Grid 중앙 좌표 얻기

#### grid_center() 메소드

<pre>
<code>
 def grid_center(self, grid_id):
 ...
 return [ctr_lon, ctr_lat]
</code>
</pre>

#### 사용

<pre>
<code>
 [ctr_lat, ctr_lon] = gridsys.grid_center(grid_id):
</code>
</pre>


### 4   임의 좌표의 그리드 중앙좌표 얻기

#### coord_center() 메소드

<pre>
<code>
 def coord_center(self, lon, lat):
 ...
 return self.grid_center(grid_id)
</code>
</pre>

#### 사용

<pre>
<code>
 [ctr_lat, ctr_lon] = coord_center(lon, lat):
</code>
</pre>
