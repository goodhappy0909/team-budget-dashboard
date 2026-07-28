import pandas as pd
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="팀 예산 관리 대시보드",
    page_icon="💰",
    layout="wide",
)

# 사이드바 설정 (필터 및 입력)
st.sidebar.title("🛠️ 예산 관리 메뉴")
selected_team = st.sidebar.selectbox(
    "팀 선택", ["전체", "개발팀", "마케팅팀", "디자인팀", "기획팀"]
)
selected_period = st.sidebar.selectbox(
    "기간 선택", ["2026년 상반기", "2026년 1분기", "2026년 2분기"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("➕ 새로운 지출 내역 추가")
with st.sidebar.form("expense_form"):
    exp_date = st.date_input("날짜")
    exp_category = st.selectbox(
        "카테고리", ["서버/인프라", "소프트웨어", "회식/복리후생", "마케팅", "기타"]
    )
    exp_amount = st.number_input("금액 (원)", min_value=0, step=10000)
    exp_memo = st.text_input("적요 (사용 내역)")
    submit_button = st.form_submit_button(label="지출 등록")

    if submit_button:
        st.sidebar.success(
            f"등록 완료: {exp_amount:,}원 ({exp_category})"
        )  # 실제 DB나 파일 연동 시 추가 로직 구현

# 메인 대시보드 화면
st.title("📊 팀 예산 관리 대시보드")
st.markdown(
    f"현재 **{selected_team}**의 **{selected_period}** 예산 집행 현황입니다."
)

# 1. 주요 지표 (Metrics) 요약
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(
        label="총 예산 (Budget)", value="50,000,000원", delta="전년 대비 +5%"
    )
with col2:
    st.metric(
        label="총 지출 (Spent)",
        value="32,450,000원",
        delta="64.9%",
        delta_color="inverse",
    )
with col3:
    st.metric(label="잔여 예산 (Remaining)", value="17,550,000원")
with col4:
    st.metric(
        label="이번 달 지출", value="4,200,000원", delta="-12%", delta_color="normal"
    )

st.markdown("---")

# 2. 예산 사용 현황 시각화 및 상세 내역
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📋 최근 지출 내역")
    # 샘플 데이터 생성
    data = {
        "날짜": ["2026-06-10", "2026-06-12", "2026-06-15", "2026-06-20"],
        "팀": ["개발팀", "마케팅팀", "개발팀", "디자인팀"],
        "카테고리": [
            "서버/인프라",
            "마케팅",
            "소프트웨어",
            "회식/복리후생",
        ],
        "적요": [
            "AWS 클라우드 비용",
            "인스타그램 광고 집행",
            "Jira 라이선스 갱신",
            "팀 워크샵",
        ],
        "금액": [1500000, 3000000, 450000, 650000],
    }
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)

with col_right:
    st.subheader("💡 카테고리별 비중")
    # 샘플 파이 차트 데이터
    category_data = pd.DataFrame(
        {
            "카테고리": [
                "서버/인프라",
                "마케팅",
                "소프트웨어",
                "회식/복리후생",
                "기타",
            ],
            "금액": [15000000, 10000000, 5000000, 2000000, 450000],
        }
    )
    st.bar_chart(category_data.set_index("카테고리"))