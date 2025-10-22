import streamlit as st
import pandas as pd
import pydeck as pdk

# 데이터 로드
file_url = 'https://raw.githubusercontent.com/sscho7/Tour/refs/heads/main/2025-TourCos.csv'
try:
    data = pd.read_csv(file_url)
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

# 지도에 필요한 칼럼만 NaN 제외로 사용
map_data = data[['명칭', '위도', '경도', '소요시간']].dropna()

# --- 제목 및 안내 ---
st.title("여행 코스 선택 및 소요시간 조회")
st.markdown("""
사이드바에서 코스명 또는 소요시간으로 필터링 가능합니다.<br>
지도에서 마우스를 올리면 각 코스의 정보가 나타납니다.
""", unsafe_allow_html=True)

# --- 사이드바: 검색 및 필터링 ---
with st.sidebar:
    st.header("여행 코스 검색/필터")
    # 코스명 텍스트 검색
    search = st.text_input("코스명으로 검색")
    filtered = map_data[map_data['명칭'].str.contains(search, case=False, na=False)]

    # 소요시간 범위 필터
    min_time = int(map_data['소요시간'].min())
    max_time = int(map_data['소요시간'].max())
    time_from, time_to = st.slider(
        "소요 시간 (분) 범위 선택",
        min_time, max_time, (min_time, max_time)
    )
    filtered = filtered[(filtered['소요시간'] >= time_from) & (filtered['소요시간'] <= time_to)]

# --- 메인 영역: 코스 선택 ---
if not filtered.empty:
    select_title = st.selectbox("여행 코스를 선택하세요.", filtered['명칭'].unique())
    selected_row = filtered[filtered['명칭'] == select_title].iloc[0]

    # 선택한 코스 정보 박스
    st.subheader("선택한 여행 코스 정보")
    st.table(pd.DataFrame(selected_row).T)
else:
    st.warning("필터링 결과가 없습니다. 검색어나 필터 조건을 다시 확인하세요.")
    selected_row = None

# --- 지도 시각화 ---
if not filtered.empty:
    v_state = pdk.ViewState(
        latitude=float(filtered['위도'].mean()),
        longitude=float(filtered['경도'].mean()),
        zoom=11 if len(filtered) > 1 else 13
    )

    color_col = [255, 80, 120, 160]  # 마커색
    # pydeck layer
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=filtered,
        get_position='[경도, 위도]',
        get_fill_color=color_col,
        get_radius=160,
        pickable=True
    )
    # pydeck map
    st.pydeck_chart(
        pdk.Deck(
            layers=[layer],
            initial_view_state=v_state,
            tooltip={"text": "{명칭}\n소요시간: {소요시간}분"}
        )
    )
else:
    st.info("지도를 표시할 데이터가 없습니다.")

# --- 데이터 표 & 다운로드 ---
st.subheader("여행 코스 데이터 (검색/필터 결과 포함)")
st.dataframe(filtered if not filtered.empty else data)

csv = (filtered if not filtered.empty else data).to_csv(index=False)
st.download_button(
    label="→ 현재 조회된 데이터 CSV 다운로드",
    data=csv,
    file_name="tour_course_filtered.csv",
    mime="text/csv"
)
