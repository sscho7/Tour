# streamlit_show_duration.py
# Streamlit 앱: CSV의 '명칭'을 선택하면 해당 항목의 '소요시간'을 보여줍니다.
# 파일 위치 기본값: /mnt/data/2025-TourCos.csv

import streamlit as st
import pandas as pd
import os
import textwrap

st.set_page_config(page_title="명칭 -> 소요시간", layout="centered")
st.title("명칭을 선택하면 소요시간을 보여줍니다")

# 기본 파일 경로 (사용자 환경에 맞게 변경 가능)
DEFAULT_CSV_PATH = "/mnt/data/2025-TourCos.csv"

st.markdown("업로드하지 않으면 기본 파일을 사용합니다: `/mnt/data/2025-TourCos.csv`")

uploaded = st.file_uploader("CSV 파일 업로드 (선택)", type=["csv"]) 

csv_path = None
if uploaded is not None:
    try:
        df = pd.read_csv(uploaded)
        csv_path = "(업로드된 파일)"
    except Exception as e:
        st.error(f"업로드한 CSV를 읽는 중 오류가 발생했습니다: {e}")
        st.stop()
else:
    if os.path.exists(DEFAULT_CSV_PATH):
        try:
            df = pd.read_csv(DEFAULT_CSV_PATH)
            csv_path = DEFAULT_CSV_PATH
        except Exception as e:
            st.error(f"기본 CSV 파일을 읽는 중 오류가 발생했습니다: {e}")
            st.stop()
    else:
        st.warning("기본 CSV 파일이 존재하지 않습니다. 파일을 업로드해주세요.")
        st.stop()

st.write(f"데이터 원본: {csv_path}")

# 도움 함수: 컬럼 이름 일치시키기
def normalize(col_name: str) -> str:
    return ''.join(ch.lower() for ch in col_name if ch.isalnum())

col_norm_map = {normalize(c): c for c in df.columns}

# 명칭 컬럼 후보 찾기
possible_name_keys = [k for k in col_norm_map.keys() if '명칭' in k or 'name' in k or 'title' in k or '명' in k]
possible_duration_keys = [k for k in col_norm_map.keys() if '소요' in k or 'duration' in k or 'time' in k or '걸' in k or '분' in k]

# 유연한 매칭: 우선 후보 사용, 없으면 전체 컬럼 선택 허용
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

# 명칭 목록 생성 (중복 제거)
names = df[name_col].dropna().astype(str).unique().tolist()

# 사용자 선택
selected_name = st.selectbox("명칭 선택", options=sorted(names))

# 선택된 명칭의 행들 필터링
matching = df[df[name_col].astype(str) == str(selected_name)]

if matching.empty:
    st.info("선택한 명칭에 해당하는 데이터가 없습니다.")
else:
    st.subheader("해당 명칭의 소요시간(들)")
    # 소요시간 칼럼을 가능한 숫자/문자 형태로 보여주기
    # 숫자형 추출 시도를 하고, 가능하면 평균/최솟값/최댓값도 표시
    dur_series = matching[duration_col]
    st.dataframe(matching[[name_col, duration_col]].reset_index(drop=True))

    # 숫자로 변환 가능한 값들 추출
    def try_parse_numeric(s):
        try:
            return pd.to_numeric(s, errors='coerce')
        except Exception:
            return pd.Series([pd.NA])

    dur_numeric = pd.to_numeric(dur_series.astype(str).str.replace('[^0-9.-]', '', regex=True), errors='coerce')
    if dur_numeric.notna().any():
        st.markdown("**숫자형으로 해석 가능한 소요시간 통계**")
        st.write(dur_numeric.describe())
        st.write(f"평균: {dur_numeric.mean():.2f} (단위: 데이터의 원본 단위 확인 필요)")
    else:
        st.info("소요시간 데이터가 숫자 형태로 파싱되지 않았습니다. 원본 단위를 확인하세요 (예: '30분', '약 1시간').")

    # 만약 여러 행이 있다면, 사용자가 특정 행을 선택할 수 있게 하기
    if len(matching) > 1:
        st.markdown("**같은 명칭에 여러 행이 있습니다. 특정 행을 선택하려면 아래에서 선택하세요.**")
        idx = st.selectbox("행 선택", options=list(matching.index), format_func=lambda i: f"행 {i}: {matching.loc[i, duration_col]}" )
        st.write("선택된 행의 소요시간:")
        st.write(matching.loc[idx, duration_col])

st.markdown("---")
st.caption(textwrap.dedent('''
설명:
- 기본적으로 `/mnt/data/2025-TourCos.csv` 파일을 읽습니다. 다른 파일을 사용하려면 상단에서 CSV를 업로드하세요.
- 코드가 자동으로 '명칭'과 '소요시간' 같은 컬럼을 찾으려 시도합니다. 컬럼명이 다른 경우 직접 선택할 수 있습니다.
- 소요시간의 단위(분/시간 등)는 원본 데이터를 확인하세요. 숫자로 변환 가능한 경우 간단한 통계(평균, 표준편차 등)를 보여줍니다.

실행:
$ streamlit run streamlit_show_duration.py
'''))
