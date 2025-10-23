import streamlit as st
import pandas as pd
import pydeck as pdk
from itertools import permutations

CSV_URL = 'https://raw.githubusercontent.com/sscho7/Tour/main/2025-TourCos.csv'

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = df.columns.str.strip()
    # 컬럼명 통일
    df = df.rename(columns={'총거리': '총 거리', '상세 정보': '상세정보'})
    return df

df = load_data()

if '위도' not in df.columns or '경도' not in df.columns:
    st.error('"위도", "경도" 컬럼이 데이터에 필요합니다. 먼저 추가해 주세요!')
    st.stop()

st.title("🗺️ 최적 여행 경로 체험")

# 1. 여러 여행지 선택할 수 있게 멀티셀렉트
places = df['명칭'].dropna().unique().tolist()
selected_places = st.multiselect(
    "경로를 그릴 여행 코스를 2개 이상 선택하세요:",
    places,
    default=places[:2]  # 예시 초기값
)

if len(selected_places) < 2:
    st.info("2개 이상 선택해야 최적 경로가 그려집니다.")
    st.stop()

# 2. 선택된 장소 좌표만 추출
sel = df[df['명칭'].isin(selected_places)].copy()
sel = sel[['명칭', '위도', '경도']].dropna()

# 3. TSP(최단순: 순열)로 최적 경로 찾기(출발-종료 고정X)
def total_dist(route):
    return sum(
        ((route[i][1] - route[i-1][1])**2 + (route[i][2] - route[i-1][2])**2) ** 0.5
        for i in range(1, len(route))
    )
place_list = sel[['명칭', '위도', '경도']].values.tolist()
min_route = min(permutations(place_list), key=total_dist)
waypoints = [dict(name=tpl[0], lat=tpl[1], lon=tpl[2]) for tpl in min_route]

# 4. 지도: 순회경로 LineLayer & 마커 모두 표시
line_data = pd.DataFrame({
    "start_lat": [waypoints[i]['lat'] for i in range(len(waypoints)-1)],
    "start_lon": [waypoints[i]['lon'] for i in range(len(waypoints)-1)],
    "end_lat":   [waypoints[i+1]['lat'] for i in range(len(waypoints)-1)],
    "end_lon":   [waypoints[i+1]['lon'] for i in range(len(waypoints)-1)],
})
marker_data = pd.DataFrame({
    "명칭":[wp["name"] for wp in waypoints],
    "위도": [wp["lat"] for wp in waypoints],
    "경도": [wp["lon"] for wp in waypoints],
    "순서": [i+1 for i in range(len(waypoints))]
})

line_layer = pdk.Layer(
    "LineLayer",
    data=line_data,
    get_source_position='[start_lon, start_lat]',
    get_target_position='[end_lon, end_lat]',
    get_width=6,
    get_color=[0, 150, 255],
    pickable=False
)
marker_layer = pdk.Layer(
    "ScatterplotLayer",
    data=marker_data,
    get_position='[경도, 위도]',
    get_color='[255, 80, 0, 200]',
    get_radius=220,
    pickable=True
)

mid = [marker_data['위도'].mean(), marker_data['경도'].mean()]

st.pydeck_chart(
    pdk.Deck(
        layers=[line_layer, marker_layer],
        initial_view_state=pdk.ViewState(
            latitude=float(mid[0]), longitude=float(mid[1]), zoom=11
        ),
        tooltip={
            "html":
                "<b>{명칭}</b><br/>"
                f"<b>순서:</b> {{순서}}<br/>"
        }
    )
)

# 5. 최적 경유 순서 및 상세 정보
st.success("이동 최적 경유 순서 (끝까지 모두 연결):")
for i, wp in enumerate(waypoints, start=1):
    info = df[df['명칭']==wp['name']].iloc[0]
    st.markdown(
        f"### {i}. {wp['name']}  "
        f"\n> **여행일정:** {info['여행일정']}  "
        f"\n> **총 거리:** {info['총 거리']}  "
        f"\n> **소요시간:** {info['소요시간']}  "
        f"\n> **상세정보:** {info['상세정보']}"
    )
