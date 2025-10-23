import streamlit as st
import pandas as pd

# 데이터 CSV 불러오기
url = 'https://raw.githubusercontent.com/sscho7/Tour/main/2025-TourCos.csv'
df = pd.read_csv(url)

# 컬럼명 확인 후, 필요한 컬럼명 변경이 필요하면 아래 주석을 참고하세요.
# df.columns = ['명칭', '여행일정', '총거리', '소요시간', '상세정보', ...]

# 명칭 목록 추출
name_list = df['명칭'].dropna().unique().tolist()

st.title("여행 코스 정보 보기")

selected_name = st.selectbox("명칭을 선택하세요", name_list)

# 선택한 명칭의 데이터 가져오기
selected_row = df[df['명칭'] == selected_name].iloc[0]

st.subheader(f"선택한 명칭: {selected_name}")

st.markdown(f"**여행일정:** {selected_row['여행일정']}")
st.markdown(f"**총거리:** {selected_row['총거리']}")
st.markdown(f"**소요시간:** {selected_row['소요시간']}")
st.markdown(f"**상세 정보:** {selected_row['상세정보']}")

