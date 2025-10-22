import streamlit as st
import pandas as pd
import pydeck as pdk

# 데이터 로드
file_path = 'https://raw.githubusercontent.com/sscho7/Tour/refs/heads/main/2025-TourCos.csv'
data = pd.read_csv(file_path)

# NaN 처리 (지도에서 사용할 컬럼만)
map_data = data[['명칭', '위도', '경도', '소요시간']].dropna()

# 1. 페이지 타이틀
st.title("여행 코스 선택 및 소요시간 조회")

# 2. 검색/필터 기능
with st.sidebar:
    st.header("여행 코스 검색 및 필터")
    # 명칭으로 검색
    search_text = st.text_input("코스명 검색")
    filtered_data = map_data[map_data['명칭'].str.contains(search_text, case=False, na=False)]
    # 소요시간 범위 슬라이더
    min_time = int(map_data['소요시간'].min())
    max_time = int(map_data['소요시간'].max())
    time_range = st.slider("소요시간(분) 범위 선택", min_time, max_time, (min_time, max_time))
    filtered_data = filtered_data[(filtered_data['소요시간'] >= time_range[0]) & (filtered_data['소요시간'] <= time_range[1])]

# 3. 여행 코스 선택(필터링된 리스트 기반)
selected_course = st.selectbox(
    "여행 코스를 선택하세요.",
    filtered_data['명칭'].unique() if not filtered_data.empty else ["해당없음"]
)

# 4. 선택된 코스 정보 추출
if selected_course != "해당없음":
    selected_location = filtered_data[filtered_data['명칭'] == selected_course].iloc[0]
    st.subheader("선택한 여행 코스 정보")
    st.write(selected_location)
else:
    st.warning("조건에 맞는 코스가 없습니다.")

# 5. pydeck 지도 시각화
if not filtered_data.empty:
    layer = pdk.Layer(
        'ScatterplotLayer',
        data=filtered_data,
        get_position='[경도, 위도]',
        get_radius=150,
        get_fill_color='[180, 0, 200, 140]',
        pickable=True
    )
    if selected_course != "해당없음":
        view_state = pdk.ViewState(
            longitude=selected_location['경도'],
            latitude=selected_location['위도'],
            zoom=12,
            pitch=0
        )
    else:  # 선택된 값이 없으면 전체 중간지점
        view_state = pdk.ViewState(
            longitude=filtered_data['경도'].mean(),
            latitude=filtered_data['위도'].mean(),
            zoom=10,
            pitch=0
        )
    st.pydeck_chart(
        pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={"text": "{명칭}\n소요시간: {소요시간}분"}
        )
    )
else:
    st.info("필터 조건에 해당하는 위치가 없습니다.")

# 6. 데이터 표 및 필터/검색 적용
st.subheader("여행 코스 전체 데이터 (검색/필터 적용)")
st.dataframe(filtered_data if not filtered_data.empty else data)

# 7. 다운로드 버튼 제공
csv = (filtered_data if not filtered_data.empty else data).to_csv(index=False)
st.download_button(
    label="검색/필터된 데이터 다운로드 (CSV)",
    data=csv,
    file_name='filtered_tour_courses.csv',
    mime='text/csv'
)
