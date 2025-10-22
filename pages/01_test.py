import streamlit as st
import pandas as pd
import pydeck as pdk

# 데이터 로드
file_path = 'https://raw.githubusercontent.com/sscho7/Tour/refs/heads/main/2025-TourCos.csv'  # 엑셀 파일의 경로
data = pd.read_csv(file_path, sheet_name='2025-TourCos')

# 데이터를 지도 포맷으로 처리
map_data = data[['명칭', '위도', '경도', '소요시간']].dropna()

# Streamlit 제목
st.title("여행 코스 선택 및 소요시간 조회")

# 지도에서 위치를 선택하도록 표시
st.subheader("아래 지도를 클릭하여 여행 코스를 선택하세요.")
selected_coords = st.map(map_data[['위도', '경도']])

# 선택된 좌표 처리
selected_location = None
if selected_coords is not None:
    selected_location = map_data.iloc[0]  # 임시로 첫 번째 데이터를 선택

    # 선택된 데이터 표시
    st.write("선택한 여행 코스 정보:")
    st.write(selected_location)

# 전체 데이터를 표 형태로 표시
st.subheader("전체 여행 코스 데이터")
st.dataframe(data)
