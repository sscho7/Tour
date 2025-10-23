import streamlit as st
import pandas as pd

# CSV 파일 경로
CSV_URL = 'https://raw.githubusercontent.com/sscho7/Tour/main/2025-TourCos.csv'

# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)
    return df

df = load_data()

st.title("🚗 2025 여행 코스 정보")

# '명칭' 셀렉트박스
name_list = df['명칭'].dropna().unique().tolist()
selected_name = st.selectbox("여행 코스를 선택하세요.", name_list)

if selected_name:
    # 선택한 명칭에 맞는 행 가져오기
    row = df[df['명칭'] == selected_name].iloc[0]

    st.markdown("---")
    st.header(f"📍 {row['명칭']}")
    st.markdown(f"**여행일정:** {row['여행일정']}")
    st.markdown(f"**총거리:** {row['총거리']}")
    st.markdown(f"**소요시간:** {row['소요시간']}")
    st.markdown(f"**상세정보:** {row['상세정보']}")
else:
    st.info("여행 코스를 선택하면 상세 정보가 나타납니다.")

# (선택) 데이터프레임 원본 확인 섹션
with st.expander("데이터 전체 보기"):
    st.dataframe(df)
