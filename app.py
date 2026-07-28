import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# 페이지 기본 설정
st.set_page_config(
    page_title="팀 예산 관리 대시보드", page_icon="💰", layout="wide"
)

# 1. 구글 스프레드시트 연결 설정
# (비밀리에 설정할 시트 주소는 잠시 뒤 시크릿 파일에 등록합니다)
conn = st.connection("gsheets", type=GSheetsConnection)

# 시트 데이터 불러오기 (ttl=0은 캐시를 남기지 않고 실시간으로 불러온다는 뜻)
df = conn.read(worksheet="지출내역", usecols=list(range(5)), ttl=0)

# 사이드바 설정
st.sidebar.title("🛠️ 예산 관리 메뉴")
selected_team = st.sidebar.selectbox(
    "팀 선택", ["전체"] + list(df["팀"].unique())
)
selected_period = st.sidebar.selectbox(
    "기간 선택", ["2026년 상반기", "2026년 1분기", "2026년 2분기"]
)

# 메인 대시보드 화면
st.title("📊 팀 예산 관리 대시보드 (Google Sheets 연동)")

# 팀 필터링 적용
if selected_team != "전체":
    filtered_df = df[df["팀"] == selected_team]
else:
    filtered_df = df

# 주요 지표 (Metrics) 요약 (스프레드시트 데이터를 기반으로 계산)
total_spent = filtered_df["금액"].sum()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="총 예산 (Budget)", value="50,000,000원")
with col2:
    st.metric(label="총 지출 (Spent)", value=f"{total_spent:,}원")
with col3:
    st.metric(label="잔여 예산 (Remaining)", value=f"{50000000 - total_spent:,}원")
with col4:
    st.metric(label="데이터 건수", value=f"{len(filtered_df)}건")

st.markdown("---")

# 상세 지출 내역 표 출력
st.subheader("📋 지출 내역 목록")
st.dataframe(filtered_df, use_container_width=True)
