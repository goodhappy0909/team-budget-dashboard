import pandas as pd
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="팀 예산 현황 및 취합 시스템", page_icon="📊", layout="wide"
)

# 세션 상태에 데이터 초기화 (브라우저 로컬스토리지 역할)
if "budget_data" not in st.session_state:
    st.session_state.budget_data = []

# 타이틀
st.markdown(
    "<h1 style='text-align: center;'>📊 팀 예산 관리 시스템</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: gray;'>부장님 보고용 월별 예산 취합 및 대시보드</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# 탭 메뉴 구현
tab1, tab2 = st.tabs(["📝 데이터 입력", "📈 전체 대시보드"])

with tab1:
    col1, col2 = st.columns([1, 2], gap="large")

    with col1:
        st.subheader("내역 입력")
        with st.form("budget_form", clear_on_submit=True):
            member = st.selectbox(
                "팀원 선택", ["부장님", "팀원1", "팀원2", "팀원3", "팀원4"]
            )
            # 기본값으로 현재 년월 설정
            current_month = pd.Timestamp.now().strftime("%Y-%m")
            month = st.text_input(
                "해당 월 (YYYY-MM)",
                value=current_month,
                placeholder="2026-06",
            )
            category = st.selectbox(
                "예산 항목", ["수선유지비", "비품", "개량공사"]
            )
            amount = st.number_input(
                "사용 금액 (원)", min_value=0, step=1000, format="%d"
            )

            submitted = st.form_submit_button(
                "기록 저장하기", use_container_width=True
            )
            if submitted:
                if month and amount > 0:
                    new_entry = {
                        "id": pd.Timestamp.now().timestamp(),
                        "날짜": month,
                        "팀원": member,
                        "항목": category,
                        "금액": amount,
                    }
                    # 최신순으로 위에 추가
                    st.session_state.budget_data.insert(0, new_entry)
                    st.success("예산 데이터가 정상적으로 기록되었습니다.")
                    st.rerun()
                else:
                    st.warning("올바른 월과 금액을 입력해주세요.")

    with col2:
        col_title, col_del = st.columns([4, 1])
        with col_title:
            st.subheader("📂 최근 입력 내역")
        with col_del:
            if st.button("모든 데이터 초기화", type="secondary"):
                st.session_state.budget_data = []
                st.success("초기화되었습니다.")
                st.rerun()

        if st.session_state.budget_data:
            df_history = pd.DataFrame(st.session_state.budget_data)

            # 화면 표시용 데이터프레임 구성
            for idx, row in df_history.iterrows():
                c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 3, 1])
                c1.write(row["날짜"])
                c2.write(row["팀원"])
                c3.markdown(f"**{row['항목']}**")
                c4.write(f"{row['금액']:,}원")
                if c5.button("🗑️", key=f"del_{row['id']}setItem"):
                    st.session_state.budget_data = [
                        item
                        for item in st.session_state.budget_data
                        if item["id"] != row["id"]
                    ]
                    st.rerun()
        else:
            st.info("등록된 데이터가 없습니다.")

with tab2:
    if not st.session_state.budget_data:
        st.warning(
            "표시할 데이터가 없습니다. '데이터 입력' 탭에서 내역을 먼저 추가해주세요."
        )
    else:
        df_all = pd.DataFrame(st.session_state.budget_data)

        # 상단 지표 카드
        total_sum = df_all["금액"].sum()
        total_count = len(df_all)

        # 이번 달 최대 사용 항목 계산
        cat_grouped = df_all.groupby("항목")["금액"].sum()
        top_cat = (
            cat_grouped.idxmax()
            if not cat_grouped.empty
            else "-"
        )
        top_cat_val = cat_grouped.max() if not cat_grouped.empty else 0

        m1, m2, m3 = st.columns(3)
        m1.metric("전체 누적 사용액", f"{total_sum:,.0f}원")
        m2.metric(
            "가장 많이 쓴 항목",
            f"{top_cat} ({top_cat_val:,.0f}원)"
            if top_cat != "-"
            else "-",
        )
        m3.metric("데이터 건수", f"{total_count}건")

        st.markdown("---")

        # 차트 영역
        c_chart1, c_chart2 = st.columns(2)

        with c_chart1:
            st.subheader("🏠 항목별 예산 분포")
            cat_df = df_all.groupby("항목")["금액"].sum().reset_index()
            # Streamlit bar chart 또는 native chart 활용
            st.bar_chart(cat_df.set_index("항목"))

        with c_chart2:
            st.subheader("👥 팀원별 누적 사용액")
            mem_df = df_all.groupby("팀원")["금액"].sum().reset_index()
            st.bar_chart(mem_df.set_index("팀원"))

        st.markdown("---")

        # 월별/항목별 요약 테이블 (취합본)
        st.subheader("📅 월별/항목별 요약 테이블 (취합본)")

        # 피벗 테이블 생성 (연월 x 항목)
        pivot_df = df_all.pivot_table(
            index="날짜",
            columns="항목",
            values="금액",
            aggfunc="sum",
            fill_value=0,
        )

        # 기본 카테고리(수선유지비, 비품, 개량공사)가 빠져있을 경우 0으로 채워주기
        for required_cat in ["수선유지비", "비품", "개량공사"]:
            if required_cat not in pivot_df.columns:
                pivot_df[required_cat] = 0

        # 필요한 컬럼 순서 정렬 및 합계 계산
        pivot_df = pivot_df[["수선유지비", "비품", "개량공사"]]
        pivot_df["합계"] = pivot_df.sum(axis=1)

        # 날짜 기준 내림차순 정렬
        pivot_df = pivot_df.sort_index(ascending=False)

        # 포맷팅 적용을 위한 복사본 혹은 그대로 출력
        st.dataframe(pivot_df.applymap(lambda x: f"{x:,.0f}원"), use_container_width=True)
