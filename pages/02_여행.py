import streamlit as st
import pandas as pd
import pydeck as pdk

CSV_URL = 'https://raw.githubusercontent.com/sscho7/Tour/main/2025-TourCos.csv'

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = df.columns.str.strip()  # 컬럼명 정리
    # 혹시 위도/경도가 문자라면 실수형으로 변환(예방적)
    if '위도' in df.columns and '경도' in df.columns:
        df['위도'] = pd.to_numeric(df['위도'], errors='coerce')
        df['경도'] = pd.to_numeric(df['경도'], errors='coerce')
    return df

df = load_data()

st.title("🗺️ 2025 여행 코스 지도")

# 실제 컬럼명 확인(디버깅용)
# st.caption("컬럼명(디버깅용):")
# st.write(df.columns.tolist())

if '위도' in df.columns and '경도' in df.columns:
    # pydeck 마커용 데이터 준비
    df_map = df[['명칭', '여행일정', '총 거리', '소요시간', '상세정보', '위도', '경도']].dropna(subset=['위도', '경도'])
    df_map = df_map.reset_index(drop=True)

    # pydeck 레이어 정의
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_map,
        get_position='[경도, 위도]',
        get_color='[0, 100, 200, 160]',
        get_radius=120,
        pickable=True
    )

    # 뷰포트(초기 중심) 지정: 첫번째 코스의 위치 기준
    midpoint = (df_map['위도'].mean(), df_map['경도'].mean())
    view_state = pdk.ViewState(
        longitude=midpoint[1], latitude=midpoint[0], zoom=10, pitch=0
    )

    st.pydeck_chart(
        pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={
                "html": """
                    <b>{명칭}</b><br>
                    <b>여행일정:</b> {여행일정}<br>
                    <b>총거리:</b> {총거리}<br>
                    <b>소요시간:</b> {소요시간}<br>
                    <b>상세정보:</b> {상세 정보}
                """,
                "style": {"color": "white"}
            }
        )
    )

    st.write("지도의 위치 아이콘을 클릭하면 세부 정보가 나옵니다.")
else:
    st.error('"위도" 및 "경도" 컬럼이 데이터에 필요합니다. CSV 파일에 두 컬럼을 추가해 주세요!')

# 데이터 전체 보기(선택)
with st.expander("🔎 전체 데이터 보기"):
    st.dataframe(df)
