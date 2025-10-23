import streamlit as st
import pandas as pd

CSV_URL = 'https://raw.githubusercontent.com/sscho7/Tour/main/2025-TourCos.csv'

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = df.columns.str.strip()  # 혹시 모를 앞뒤 공백, 탭, 줄바꿈 제거
    return df

df = load_data()

st.title("🚗 2025 여행 코스 정보")

# 실제 컬럼명을 출력해 확인한다
st.caption("컬럼명(디버깅용):")
st.write(df.columns.tolist())      # 여기에 ['명칭', '여행일정', ..., '상세 정보']처럼 나옵니다

# '명칭' 컬럼에서 고유값만 추출, 셀렉트박스 생성
name_list = df['명칭'].dropna().unique().tolist()
selected_name = st.selectbox("여행 코스를 선택하세요.", name_list)

if selected_name:
    row = df[df['명칭'] == selected_name].iloc[0]

    st.markdown("---")
    st.header(f"📍 {row['명칭']}")
    st.markdown(f"**여행일정:** {row['여행일정']}")
    st.markdown(f"**총거리:** {row['총거리']}")
    st.markdown(f"**소요시간:** {row['소요시간']}")
    st.markdown(f"**상세정보:** {row['상세 정보']}")   # ←←← 반드시 띄어쓰기 반영!
else:
    st.info("여행 코스를 선택하면 상세 정보가 나타납니다.")

# 원본 데이터 전체 보기(선택적)
with st.expander("🔎 전체 데이터프레임 보기"):
    st.dataframe(df)
