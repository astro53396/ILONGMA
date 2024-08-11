import math
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
import contextily as ctx
from geopy.distance import great_circle
from pyproj import CRS
from matplotlib.widgets import Slider

# 1. CSV 파일에서 누출지점 위치 데이터 읽어오기
rocket_trajectory = pd.read_csv('rocket_trajectory.csv')

# CSV 파일의 열 이름이 다를 수 있으니 실제 열 이름을 확인해야 합니다.
rocket_trajectory = rocket_trajectory.rename(columns={
    'Time (s)': 'time',
    'Latitude (°)': 'lat',
    'Longitude (°)': 'lon'
})

# 시간 열을 datetime 형식으로 변환 (필요시)
rocket_trajectory['time'] = pd.to_datetime(rocket_trajectory['time'], unit='s', origin='unix')

# 확인
print(rocket_trajectory)

# 누출지점 위치 데이터로 사용
df_pt = rocket_trajectory.copy()

# 변수 이름을 동일하게 유지
time_points = df_pt['time']  # 시간 정보

# 누출지점 포인트 공간 데이터 생성
gdf_pt_geom = gpd.GeoDataFrame(df_pt, geometry=gpd.points_from_xy(df_pt.lon, df_pt.lat), crs=CRS.from_epsg(4326))
gdf_pt3857 = gdf_pt_geom.to_crs(epsg=3857)

# 2. 누출지점 주변 격자 생성
# 범위 설정
xmin = gdf_pt3857.geometry.x.min() - 3000
xmax = gdf_pt3857.geometry.x.max() + 3000
ymin = gdf_pt3857.geometry.y.min() - 3000
ymax = gdf_pt3857.geometry.y.max() + 3000

# 격자 크기
wide = 50
length = 50
cols = list(range(int(np.floor(xmin)), int(np.ceil(xmax)), wide))
rows = list(range(int(np.floor(ymin)), int(np.ceil(ymax)), length))
rows.reverse()

# 격자 폴리곤 생성
polygons = []
for x in cols:
    for y in rows:
        polygons.append(Polygon([(x, y), (x + wide, y), (x + wide, y - length), (x, y - length)]))

grid3857 = gpd.GeoDataFrame({'geometry': polygons}, crs="epsg:3857")
grid4326 = grid3857.to_crs(epsg=4326)

# 평면 좌표계로 변환하여 centroid 계산
grid3857['grid_lon'] = grid3857.centroid.x
grid3857['grid_lat'] = grid3857.centroid.y


# 3. 시간별 오염도 계산 함수
def calculate_pollutant_concentration(df_pt, direction, a, b, k):
    cumulative_level = pd.Series(np.zeros(len(grid3857)), index=grid3857.index)  # 누적 오염도 초기화
    concentrations = []
    
    for idx, point in df_pt.iterrows():
        # 누출지점 좌표를 GeoDataFrame으로 변환
        gdf_pt = gpd.GeoDataFrame({'geometry': gpd.points_from_xy([point['lon']], [point['lat']])}, crs=CRS.from_epsg(4326))
        gdf_pt3857 = gdf_pt.to_crs(epsg=3857)
        
        # 거리 및 각도 계산
        merged = grid4326.copy()
        merged['dist'] = merged.apply(
            lambda x: great_circle((point['lat'], point['lon']), (x.geometry.centroid.y, x.geometry.centroid.x)).meters,
            axis=1
        )
        merged['angle'] = merged.apply(
            lambda x: np.arctan2(x.geometry.centroid.x - point['lon'], x.geometry.centroid.y - point['lat']),
            axis=1
        )
        
        # 오염도 계산
        merged['level'] = merged.apply(
            lambda x: a * math.exp(
                -((x['dist'] / b) ** 2) * (math.exp(-k * math.cos(x['angle'] - direction))) ** 2
            ), axis=1
        )
        
        # grid3857에 level 열 추가
        grid_with_level = grid3857.join(merged[['level']], how='left')
        
        # 누적 오염도 계산
        cumulative_level += grid_with_level['level'].fillna(0)
        concentrations.append(cumulative_level.copy())
    
    return concentrations

direction = -30 * math.pi / 180  # 풍향
a = 10000  # 누출지점의 오염도
b = 200    # 거리 척도
k = 2.5    # 이심률

# 시간별 오염도 계산
concentration_maps = calculate_pollutant_concentration(df_pt, direction, a, b, k)

# 4. 시각화: 슬라이더를 사용하여 결과 탐색
fig, ax = plt.subplots(figsize=(30, 30))
plt.subplots_adjust(left=0.1, bottom=0.2)
s = Slider(plt.axes([0.1, 0.1, 0.65, 0.03]), 'Time', 0, len(concentration_maps) - 1, valinit=0, valfmt='%d')

# 초기 컬러바 객체
sm = plt.cm.ScalarMappable(cmap='Reds', norm=plt.Normalize(vmin=0, vmax=10000))
cbar = fig.colorbar(sm, ax=ax, orientation='vertical')

def update(val):
    index = int(s.val)
    cumulative_map = concentration_maps[index]
    
    # 데이터 플롯
    ax.clear()  # 기존 플롯을 제거하고 새로 그리기
    
    # 새로 생성된 격자 데이터를 배경으로 플로팅
    grid3857['level'] = cumulative_map
    grid3857.plot(column='level', cmap='Reds', ax=ax, alpha=0.5, legend=False)
    
    # 누출 지점 표시
    gdf_pt3857[gdf_pt3857['time'] <= df_pt['time'].iloc[index]].plot(ax=ax, color='red', markersize=100, label='Leak Point')
    
    # 베이스맵 추가
    ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron, crs='EPSG:3857')
    
    # 레이블, 타이틀 설정
    ax.set_axis_off()
    ax.grid(False)
    ax.legend()  # 'Leak Point' 레이블 추가
    plt.title(f'Pollutant Concentration on {df_pt["time"].iloc[index].strftime("%Y-%m-%d %H:%M:%S")}')
    
    # 축 범위 고정
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    
    plt.draw()

def strt():
    s.on_changed(update)
    update(0)  # 초기화
    plt.show()

strt()

