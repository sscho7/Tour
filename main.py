# streamlit_show_duration.py
# Streamlit 앱: CSV의 '명칭'을 선택하면 해당 항목의 '소요시간'을 보여줍니다.
# 데이터는 GitHub에 업로드된 CSV를 직접 불러옵니다.

import streamlit as st
import pandas as pd
import textwrap

st.set_page_config(page_title="명칭 -> 소요시간", layout="centered")
st.title("명칭을 선택하면 소요시간을 보여줍니다")

# ✅ GitHub에 있는 CSV 파일 불러오기
URL = "https://raw.githubusercontent.com/sscho7/Tour/main/2025-TourCos.csv"
try:
    df = pd.read_csv(URL)
    st.success("GitHub에서 데이터를 성공적으로 불러왔습니다 ✅")
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류 발생: {e}")
    st.stop()

# 컬럼 이름 표준화 함수
def normalize(col_name: str) -> str:
    return ''.join(ch.lower() for ch in col_name if ch.isalnum())

col_norm_map = {normalize(c): c for c in df.columns}

# 명칭 및 소요시간 컬럼 자동 탐색
possible_name_keys = [k for k in col_norm_map.keys() if '명칭' in k or 'name' in k or 'title' in k or '명' in k]
possible_duration_keys = [k for k in col_norm_map.keys() if '소요' in k or 'duration' in k or 'time' in k or '걸' in k or '분' in k]

# 자동 감지 or 수동 선택
if possible_name_keys:
    name_col_key = possible_name_keys[0]
    name_col = col_norm_map[name_col_key]
else:
    name_col = st.selectbox("명칭으로 사용할 컬럼을 선택하세요", options=list(df.columns))

if possible_duration_keys:
    duration_col_key = possible_duration_keys[0]
    duration_col = col_norm_map[duration_col_key]
else:
    duration_col = st.selectbox("소요시간(또는 duration)으로 사용할 컬럼을 선택하세요", options=list(df.columns))

st.write("선택된 컬럼:")
st.write(f"- 명칭: **{name_col}**\n- 소요시간: **{duration_col}**")

# 명칭 목록 생성
names = df[name_col].dropna().astype(str).unique().tolist()

# 사용자 명칭 선택
selected_name = st.selectbox("명칭 선택", options=sorted(names))

# 선택된 명칭의 행 필터링
matching = df[df[name_col].astype(str) == str(selected_name)]

if matching.empty:
    st.info("선택한 명칭에 해당하는 데이터가 없습니다.")
else:
    st.subheader("해당 명칭의 소요시간(들)")
    dur_series = matching[duration_col]
    st.dataframe(matching[[name_col, duration_col]].reset_index(drop=True))

    # 숫자 변환 시도
    dur_numeric = pd.to_numeric(dur_series.astype(str).str.replace('[^0-9.-]', '', regex=True), errors='coerce')
    if dur_numeric.notna().any():
        st.markdown("**숫자형으로 해석 가능한 소요시간 통계**")
        st.write(dur_numeric.describe())
        st.write(f"평균: {dur_numeric.mean():.2f} (단위: 데이터의 원본 단위 확인 필요)")
    else:
        st.info("소요시간 데이터가 숫자 형태로 파싱되지 않았습니다. (예: '30분', '약 1시간')")

    # 여러 행일 경우 개별 선택 옵션
    if len(matching) > 1:
        st.markdown("**같은 명칭에 여러 행이 있습니다. 특정 행을 선택하려면 아래에서 선택하세요.**")
        idx = st.selectbox("행 선택", options=list(matching.index), format_func=lambda i: f"행 {i}: {matching.loc[i, duration_col]}")
        st.write("선택된 행의 소요시간:")
        st.write(matching.loc[idx, duration_col])

st.markdown("---")
st.caption(textwrap.dedent('''
설명:
- GitHub에서 CSV 파일(`https://github.com/sscho7/Tour/blob/main/2025-TourCos.csv`)을 직접 읽어옵니다.
- 코드가 자동으로 '명칭'과 '소요시간' 컬럼을 탐색합니다. 컬럼명이 다르면 직접 선택 가능합니다.
- 소요시간 데이터는 숫자로 변환 가능한 경우 통계를 제공합니다.

실행:
$ streamlit run streamlit_show_duration.py
'''))
