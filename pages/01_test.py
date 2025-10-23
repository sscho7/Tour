import streamlit as st
import pandas as pd
import pydeck as pdk

CSV_URL = 'https://raw.githubusercontent.com/sscho7/Tour/main/2025-TourCos.csv'

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = df.columns.str.strip()
    return df

df = load_data()

st.title("🚗 2025 여행 코스 정보")

# 컬럼명 확인
st.caption("컬럼명(디버깅용):")
st.write(df.columns.tolist())

# 위도/경도 컬럼의 존재 확인
if '위도' in df.columns and '경도' in df.columns:
    # 결측치 제거 및 타입 변환
    df['위도'] = pd.to_numeric(df['위도'], errors='coerce')
    df['경도'] = pd.to_numeric(df['경도'], errors='coerce')
    df_map = df.dropna(subset=['위도', '경도']).copy()

    st.subheader("🗺 여행 코스 지도")
    # pydeck Layer
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_map,
        get_position='[경도, 위도]',
        get_color='[200, 30, 0, 160]',
        get_radius=200,
        pickable=True
    )
    view_state = pdk.ViewState(
        longitude=float(df_map['경도'].mean()),
        latitude=float(df_map['위도'].mean()),
        zoom=11
    )
    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={
            "html": "<b>{명칭}</b><br/>"
                    "<b>여행일정:</b> {여행일정}<br/>"
                    "<b>총 거리:</b> {총 거리}<br/>"
                    "<b>소요시간:</b> {소요시간}<br/>"
                    "<b>상세정보:</b> {상세정보}"
        }
    )
    st.pydeck_chart(r)

    st.info("지도 위 마커를 클릭하면 세부 정보가 표시됩니다.")

else:
    st.warning('CSV 파일에 "위도", "경도" 컬럼(열)이 추가되어야 지도에 마커가 표시됩니다!')

# 아래는 상세 정보 또는 데이터 전체 보기
name_list = df['명칭'].dropna().unique().tolist()
selected_name = st.selectbox("여행 코스를 선택하세요.", name_list)

if selected_name:
    row = df[df['명칭'] == selected_name].iloc[0]
    st.markdown("---")
    st.header(f"📍 {row['명칭']}")
    st.markdown(f"**여행일정:** {row['여행일정']}")
    st.markdown(f"**총거리:** {row['총거리']}")
    st.markdown(f"**소요시간:** {row['소요시간']}")
    st.markdown(f"**상세정보:** {row['상세 정보']}")
else:
    st.info("여행 코스를 선택하면 상세 정보가 나타납니다.")

with st.expander("🔎 전체 데이터프레임 보기"):
    st.dataframe(df)
