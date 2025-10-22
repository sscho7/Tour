import streamlit as st
import pandas as pd
import pydeck as pdk

# 데이터 로드
file_path = 'https://raw.githubusercontent.com/sscho7/Tour/refs/heads/main/2025-TourCos.csv'
data = pd.read_csv(file_path)

# NaN 처리
map_data = data[['명칭', '위도', '경도', '소요시간']].dropna()

# Streamlit 제목
st.title("여행 코스 선택 및 소요시간 조회")

# 코스 명칭 리스트 선택
selected_course = st.selectbox("여행 코스를 선택하세요.", map_data['명칭'].unique())

# 선택된 코스 정보 추출
selected_location = map_data[map_data['명칭'] == selected_course].iloc[0]

# 선택된 코스 정보 표시
st.subheader("선택한 여행 코스 정보")
st.write(selected_location)

# 지도 표시 (선택한 포인트에 마커 표시)
layer = pdk.Layer(
    'ScatterplotLayer',
    data=map_data,
    get_position='[경도, 위도]',
    get_radius=100,
    get_fill_color='[180, 0, 200, 140]',
    pickable=True
)

view_state = pdk.ViewState(
    longitude=selected_location['경도'],
    latitude=selected_location['위도'],
    zoom=12,
    pitch=0
)

st.pydeck_chart(
    pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "{명칭}\n소요시간: {소요시간}분"}
    )
)

# 전체 데이터 표시
st.subheader("전체 여행 코스 데이터")
st.dataframe(data)
