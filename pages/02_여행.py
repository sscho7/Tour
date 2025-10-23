import streamlit as st
import pandas as pd
import pydeck as pdk

CSV_URL = 'https://raw.githubusercontent.com/sscho7/Tour/main/2025-TourCos.csv'

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = df.columns.str.strip()
    # 위도/경도가 존재할 때만 변환
    if '위도' in df.columns and '경도' in df.columns:
        df['위도'] = pd.to_numeric(df['위도'], errors='coerce')
        df['경도'] = pd.to_numeric(df['경도'], errors='coerce')
    return df

df = load_data()

st.title("🗺️ 2025 여행 코스 지도")

# ① 컬럼명 확인
st.write("컬럼명:", df.columns.tolist())
# ② 위도, 경도 샘플 확인
if '위도' in df.columns and '경도' in df.columns:
    st.dataframe(df[['명칭', '위도', '경도']])
    st.write("위도 결측치 수:", df['위도'].isnull().sum())
    st.write("경도 결측치 수:", df['경도'].isnull().sum())
    st.write("위도 타입:", df['위도'].dtype, ", 경도 타입:", df['경도'].dtype)

    df_map = df.dropna(subset=['위도', '경도']).copy()

    # 데이터가 1개 이상이면 지도 표시!
    if len(df_map) > 0:
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df_map,
            get_position='[경도, 위도]',
            get_color='[0, 100, 200, 160]',
            get_radius=250,
            pickable=True
        )
        midpoint = (df_map['위도'].mean(), df_map['경도'].mean())
        view_state = pdk.ViewState(
            longitude=float(midpoint[1]), latitude=float(midpoint[0]), zoom=10, pitch=0
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
    else:
        st.warning("위도, 경도가 모두 있는 데이터가 없습니다. 마커가 표시되지 않습니다.")
else:
    st.error('"위도"와 "경도" 컬럼이 없습니다. 컬럼명을 정확하게 맞춰주세요.')

with st.expander("🔎 전체 데이터 보기"):
    st.dataframe(df)
