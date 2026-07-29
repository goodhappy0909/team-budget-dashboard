import pandas as pd
import requests
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="팀 예산 현황 및 취합 시스템 (DB 연동)",
    page_icon="📊",
    layout="wide",
)

GAS_WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzUMMQcmzzYAkmLF-urvol4-tocFISIgtYYQW7whzfSI2SYEcHX0pwx-D2ETAn8Fib-cw/exec"


def fetch_data_from_sheet():
    """구글 시트에서 전체 데이터 조회"""
    try:
        response = requests.get(f"{GAS_WEB_APP_URL}?action=select", timeout=10)
        result = response.json()
        if result.get("status") == "success":
            return result.get("data", [])
    except Exception as e:
        st.error(f"데이터 조회 중 통신 오류 발생: {e}")
    return []


def insert_data_to_sheet(entry):
    """구글 시트에 새로운 데이터 추가"""
    try:
        payload = {
            "action": "insert",
            "data": {
                "id": str(entry["id"]),
                "날짜": str(entry["날짜"]),
                "팀원": str(entry["팀원"]),
                "항목": str(entry["항목"]),
                "금액": int(entry["금액"]),
            },
        }
        response = requests.post(GAS_WEB_APP_URL, json=payload, timeout=10)
        result = response.json()
        
        if result.get("status") == "success":
            return True, ""
        else:
            return False, result.get("message", "알 수 없는 서버 에러")
    except Exception as e:
        return False, str(e)


def delete_data_from_sheet(row_id):
    """구글 시트에서 특정 데이터 삭제 (id 기준)"""
    try:
        payload = {
            "action": "delete",
            "idColumn": "id",
            "idValue": str(row_id),
        }
        response = requests.post(GAS_WEB_APP_URL, json=payload, timeout=10)
        result = response.json()
        return result.get("status") == "success"
    except Exception as e:
        st.error(f"데이터 삭제 중 오류 발생: {e}")
        return False


# 세션 상태 초기화
if "budget_data" not in st.session_state:
    st.session_state.budget_data = fetch_data_from_sheet()

# 타이틀
st.markdown(
    "<h1 style='text-align: center;'>📊 팀 예산 관리 시스템 (Google Sheets DB)</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: gray;'>부장님 보고용 월별 예산 취합 및 대시보드</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

tab1, tab2 = st.tabs(["📝 데이터 입력", "📈 전체 대시보드"])

with tab1:
    col1, col2 = st.columns([1, 2], gap="large")

    with col1:
        st.subheader("내역 입력")
        with st.form("budget_form", clear_on_submit=True):
            member = st.selectbox(
                "팀원 선택", ["부장님", "팀원1", "팀원2", "팀원3", "팀원4"]
            )
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
                        "id": int(pd.Timestamp.now().timestamp() * 1000),
                        "날짜": month,
                        "팀원": member,
                        "항목": category,
                        "금액": amount,
                    }
                    
                    success, err_msg = insert_data_to_sheet(new_entry)
                    if success:
                        st.success("구글 시트에 정상적으로 기록되었습니다!")
                        st.session_state.budget_data = fetch_data_from_sheet()
                        st.rerun()
                    else:
                        st.error(f"저장에 실패했습니다. (상세 사유: {err_msg})")
                else:
                    st.warning("올바른 월과 금액을 입력해주세요.")

    with col2:
        col_title, col_refresh = st.columns([4, 1])
        with col_title:
            st.subheader("📂 최근 입력 내역")
        with col_refresh:
            if st.button("🔄 새로고침", type="secondary"):
                st.session_state.budget_data = fetch_data_from_sheet()
                st.rerun()

        if not st.session_state.budget_data:
            st.session_state.budget_data = fetch_data_from_sheet()

        if st.session_state.budget_data:
            df_history = pd.DataFrame(st.session_state.budget_data)

            for idx, row in df_history.iloc[::-1].iterrows():
                c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 3, 1])
                c1.write(str(row.get("날짜", "")))
                c2.write(str(row.get("팀원", "")))
                c3.markdown(f"**{row.get('항목', '')}**")
                
                try:
                    amt_val = int(float(row.get("금액", 0)))
                except:
                    amt_val = 0
                c4.write(f"{amt_val:,}원")

                if c5.button("🗑️", key=f"del_{row.get('id', idx)}"):
                    row_id = row.get("id")
                    if delete_data_from_sheet(row_id):
                        st.success("삭제되었습니다.")
                        st.session_state.budget_data = fetch_data_from_sheet()
                        st.rerun()
                    else:
                        st.error("삭제 실패")
        else:
            st.info("등록된 데이터가 없습니다.")

with tab2:
    st.session_state.budget_data = fetch_data_from_sheet()

    if not st.session_state.budget_data:
        st.warning(
            "표시할 데이터가 없습니다. '데이터 입력' 탭에서 내역을 먼저 추가해주세요."
        )
    else:
        df_all = pd.DataFrame(st.session_state.budget_data)
        df_all["금액"] = pd.to_numeric(df_all["금액"], errors="coerce").fillna(0)

        total_sum = df_all["금액"].sum()
        total_count = len(df_all)

        cat_grouped = df_all.groupby("항목")["금액"].sum()
        top_cat = cat_grouped.idxmax() if not cat_grouped.empty else "-"
        top_cat_val = cat_grouped.max() if not cat_grouped.empty else 0

        m1, m2, m3 = st.columns(3)
        m1.metric("전체 누적 사용액", f"{total_sum:,.0f}원")
        m2.metric(
            "가장 많이 쓴 항목",
            f"{top_cat} ({top_cat_val:,.0f}원)" if top_cat != "-" else "-",
        )
        m3.metric("데이터 건수", f"{total_count}건")

        st.markdown("---")

        c_chart1, c_chart2 = st.columns(2)

        with c_chart1:
            st.subheader("🏠 항목별 예산 분포")
            cat_df = df_all.groupby("항목")["금액"].sum().reset_index()
            st.bar_chart(cat_df.set_index("항목"))

        with c_chart2:
            st.subheader("👥 팀원별 누적 사용액")
            mem_df = df_all.groupby("팀원")["금액"].sum().reset_index()
            st.bar_chart(mem_df.set_index("팀원"))

        st.markdown("---")

        st.subheader("📅 월별/항목별 요약 테이블 (취합본)")

        pivot_df = df_all.pivot_table(
            index="날짜",
            columns="항목",
            values="금액",
            aggfunc="sum",
            fill_value=0,
        )

        for required_cat in ["수선유지비", "비품", "개량공사"]:
            if required_cat not in pivot_df.columns:
                pivot_df[required_cat] = 0

        pivot_df = pivot_df[["수선유지비", "비품", "개량공사"]]
        pivot_df["합계"] = pivot_df.sum(axis=1)
        pivot_df = pivot_df.sort_index(ascending=False)

        st.dataframe(
            pivot_df.map(lambda x: f"{x:,.0f}원"), use_container_width=True
        )
