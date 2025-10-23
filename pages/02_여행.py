import streamlit as st
import pandas as pd
import pydeck as pdk
import re

CSV_URL = 'https://raw.githubusercontent.com/sscho7/Tour/main/2025-TourCos.csv'

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = df.columns.str.strip()
    df = df.rename(columns={'총거리': '총 거리', '상세 정보': '상세정보'})
    return df

df = load_data()

if '위도' not in df.columns or '경도' not in df.columns:
    st.error('"위도", "경도" 컬럼이 데이터에 필요합니다. 먼저 추가해 주세요!')
    st.stop()

st.title("🗺️ 상세정보 순서 기반 여행 경로 시각화")

# 1. 여행 코스(명칭) 하나 선택
course_names = df['명칭'].dropna().unique().tolist()
selected_course = st.selectbox("경로를 보고 싶은 여행 코스를 선택하세요.", course_names)

row = df[df['명칭'] == selected_course].iloc[0]
st.subheader(f"상세정보\n\n{row['상세정보']}")

# 2. 상세정보란에서 "1. ~", "2. ~", ... 패턴으로 여행지명만 추출
def extract_places(text):
    # 1. 여행지명(공백포함) 2. 여행지명 ... 의 '여행지명'만 추출
    items = re.findall(r'\d+\.\s*([^\d\.]+)', text)
    return [item.strip() for item in items]

route_places = extract_places(row['상세정보'])

st.write("상세정보에 기재된 경유지 순서:", route_places)

# 3. 각 여행지명의 위도/경도 추출 (전체 df에서 검색)
points = []
for place in route_places:
    match = df[df['명칭'].str.strip() == place]
    if not match.empty and pd.notnull(match.iloc[0]["위도"]) and pd.notnull(match.iloc[0]["경도"]):
        points.append({
            "명칭": place,
            "위도": match.iloc[0]["위도"],
            "경도": match.iloc[0]["경도"]
        })
    else:
        st.warning(f"여행지 [{place}]의 위치 정보가 데이터에 없습니다.")

if len(points) < 2:
    st.error("2곳 이상의 경유지가 있어야 경로를 그릴 수 있습니다.")
    st.stop()

# 4. 경로 시각화(pydeck)
route_df = pd.DataFrame(points)
# 마커 데이터프레임(순서)
marker_data = route_df.copy()
marker_data["순서"] = marker_data.index + 1
# 라인 접합부 포인트 쌍
line_data = pd.DataFrame({
    "start_lat": route_df["위도"][:-1],
    "start_lon": route_df["경도"][:-1],
    "end_lat":   route_df["위도"][1:],
    "end_lon":   route_df["경도"][1:],
})

line_layer = pdk.Layer(
    "LineLayer",
    data=line_data,
    get_source_position='[start_lon, start_lat]',
    get_target_position='[end_lon, end_lat]',
    get_width=5,
    get_color=[0, 100, 255],
    pickable=False
)
marker_layer = pdk.Layer(
    "ScatterplotLayer",
    data=marker_data,
    get_position='[경도, 위도]',
    get_color='[255, 80, 0, 200]',
    get_radius=200,
    pickable=True
)

mid = (route_df["위도"].mean(), route_df["경도"].mean())
st.pydeck_chart(
    pdk.Deck(
        layers=[line_layer, marker_layer],
        initial_view_state=pdk.ViewState(
            latitude=float(mid[0]), longitude=float(mid[1]), zoom=12
        ),
        tooltip={
            "html": "<b>{명칭}</b><br/>"
                    "<b>순서:</b> {순서}"
        }
    )
)

# 5. 상세정보와 각 포인트 정보
st.success("경로 상세 순서 및 위치:")
for i, pt in enumerate(points, 1):
    st.markdown(f"### {i}. {pt['명칭']}\n> 위도: {pt['위도']}  /  경도: {pt['경도']}")
