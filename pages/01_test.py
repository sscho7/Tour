import streamlit as st
import pandas as pd
import pydeck as pdk

# Google Map 미리보기 embed 함수
def show_google_map(lat, lon, zoom=16, width='100%', height=400):
    url = f"https://www.google.com/maps?q={lat},{lon}&z={zoom}&output=embed"
    st.components.v1.iframe(url, width=width, height=height, scrolling=False)

CSV_URL = 'https://raw.githubusercontent.com/sscho7/Tour/main/2025-TourCos.csv'

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = df.columns.str.strip()
    return df

df = load_data()

st.title("🗺️ 2025 여행 코스 지도 & 상세정보")

# 지도+마커 표시 (위도/경도 체크)
if '위도' in df.columns and '경도' in df.columns:
    df['위도'] = pd.to_numeric(df['위도'], errors='coerce')
    df['경도'] = pd.to_numeric(df['경도'], errors='coerce')
    df_map = df.dropna(subset=['위도', '경도'])

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_map,
        get_position='[경도, 위도]',
        get_color='[200, 30, 0, 160]',
        get_radius=200,
        pickable=True
    )
    midpoint = (df_map['위도'].mean(), df_map['경도'].mean())
    view_state = pdk.ViewState(
        longitude=float(midpoint[1]), latitude=float(midpoint[0]), zoom=11
    )
    st.pydeck_chart(
        pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={
                "html": "<b>{명칭}</b><br/>"
                        "<b>여행일정:</b> {여행일정}<br/>"
                        "<b>총거리:</b> {총 거리}<br/>"
                        "<b>소요시간:</b> {소요시간}<br/>"
                        "<b>상세 정보:</b> {상세 정보}"
            }
        )
    )
    st.info("지도 위 마커에 마우스를 올리면 주요 정보 툴팁이 표시됩니다.")

# 여행지 선택
name_list = df['명칭'].dropna().unique().tolist()
selected_name = st.selectbox("여행 코스를 선택하세요.", name_list)

if selected_name:
    row = df[df['명칭'] == selected_name].iloc[0]
    st.markdown("---")
    st.header(f"📍 {row['명칭']}")
    st.markdown(f"**여행일정:** {row['여행일정']}")
    st.markdown(f"**총거리:** {row['총 거리']}")
    st.markdown(f"**소요시간:** {row['소요시간']}")
    st.markdown(f"**상세정보:** {row['상세 정보']}")

    # Google Map 미리보기 내장 표시
    if '위도' in row and '경도' in row and pd.notnull(row['위도']) and pd.notnull(row['경도']):
        st.subheader("📌 실제 위치 주변 지도 미리보기 (Google Maps)")
        show_google_map(row['위도'], row['경도'])
        map_link = f"https://maps.google.com/?q={row['위도']},{row['경도']}"
        st.markdown(f"[구글맵에서 크게 보기]({map_link})")
    else:
        st.info("이 코스는 위도/경도 정보가 없어 지도를 표시할 수 없습니다.")

else:
    st.info("여행 코스를 선택하면 상세 정보와 실제 위치 지도가 표시됩니다.")

with st.expander("🔎 전체 데이터프레임 보기"):
    st.dataframe(df)
