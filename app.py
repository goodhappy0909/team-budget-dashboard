import json
import urllib.parse
import urllib.request
import pandas as pd
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="팀 예산 관리 시스템",
    page_icon="📊",
    layout="wide",
)

# 🔗 Google Apps Script 웹 앱 URL
GAS_WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzUMMQcmzzYAkmLF-urvol4-tocFISIgtYYQW7whzfSI2SYEcHX0pwx-D2ETAn8Fib-cw/exec"


def call_gas_api(params):
    """구글 Apps Script 통신 함수"""
    try:
        query_string = urllib.parse.urlencode(params)
        full_url = f"{GAS_WEB_APP_URL}?{query_string}"

        req = urllib.request.Request(
            full_url, headers={"User-Agent": "Mozilla/5.0"}
        )

        with urllib.request.urlopen(req, timeout=15) as response:
            res_data = response.read().decode("utf-8")
            return json.loads(res_data)
    except Exception as e:
        return {"status": "error", "message": str(e)}


def fetch_data_from_sheet():
    """구글 시트 전체 데이터 가져오기"""
    res = call_gas_api({"action": "select"})
    if res.get("status") == "success":
        return res.get("data", [])
    return []


def insert_data_to_sheet(entry):
    """구글 시트에 데이터 추가하기"""
    data_json = json.dumps(
        {
            "id": str(entry["id"]),
            "날짜": str(entry["날짜"]),
            "팀원": str(entry["팀원"]),
            "항목": str(entry["항목"]),
            "금액": int(entry["금액"]),
        },
        ensure_ascii=False,
    )

    params = {"action": "insert", "data": data_json}
    res = call_gas_api(params)

    if res.get("status") == "success":
        return True, ""
    else:
        return False, res.get("message", "저장 실패")


def delete_data_from_sheet(row_id):
    """구글 시트에서 특정 데이터 삭제하기"""
    params = {"action": "delete", "idColumn": "id", "idValue": str(row_id)}
    res = call_gas_api(params)
    return res.get("status") == "success"


def generate_budget_report(df):
    """현재 예산 데이터를 분석하여 브리핑 보고서 생성"""
    if df.empty:
        return "등록된 데이터가 없어 예산을 집계할 수 없습니다."

    # 숫자 데이터 정제
    df["금액"] = pd.to_numeric(df["금액"], errors="coerce").fillna(0)

    total_sum = df["금액"].sum()
    total_count = len(df)
    avg_amount = total_sum / total_count if total_count > 0 else 0

    # 항목별 집계
    cat_summary = df.groupby("항목")["금액"].sum().sort_values(ascending=False)
    top_cat = cat_summary.index[0] if not cat_summary.empty else "-"
    top_cat_amt = cat_summary.iloc[0] if not cat_summary.empty else 0
    top_cat_ratio = (top_cat_amt / total_sum * 100) if total_sum > 0 else 0

    # 팀원별 집계
    member_summary = (
        df.groupby("팀원")["금액"].sum().sort_values(ascending=False)
    )
    top_member = member_summary.index[0] if not member_summary.empty else "-"
    top_member_amt = member_summary.iloc[0] if not member_summary.empty else 0
    top_member_ratio = (
        (top_member_amt / total_sum * 100) if total_sum > 0 else 0
    )

    # 텍스트 리포트 생성
    report = f"""
    ### 📢 예산 집계 및 요약 브리핑
    ---
    #### 1. 핵심 지표 요약
    * **총 집계 지출액**: **`{total_sum:,.0f}원`** (총 {total_count}건 등록)
    * **1건당 평균 지출액**: `{avg_amount:,.0f}원`
    
    #### 2. 주요 분석 인사이트
    * **최다 지출 항목**: **`{top_cat}`** 
      * 지출액: `{top_cat_amt:,.0f}원` (전체 지출의 **{top_cat_ratio:.1f}%** 차지)
    * **최다 지출 팀원**: **`{top_member}`**
      * 지출액: `{top_member_amt:,.0f}원` (전체 지출의 **{top_member_ratio:.1f}%** 차지)
    
    #### 3. 항목별 상세 지출 현황
    """

    for cat, amt in cat_summary.items():
        ratio = (amt / total_sum * 100) if total_sum > 0 else 0
        report += f"\n    * **{cat}**: `{amt:,.0f}원` ({ratio:.1f}%)"

    report += "\n\n    #### 4. 팀원별 상세 지출 현황"
    for mem, amt in member_summary.items():
        ratio = (amt / total_sum * 100) if total_sum > 0 else 0
        report += f"\n    * **{mem}**: `{amt:,.0f}원` ({ratio:.1f}%)"

    report += f"""
    
    ---
    💡 **관리자 가이드**: 
    현재 가장 지출 비중이 높은 항목은 **[{top_cat}]**입니다. 월별 예산 한도 대비 차이가 큰 경우 해당 항목의 상세 영수증 내역 검토를 권장합니다.
    """
    return report


# 데이터 세션 상태 초기화
if "budget_data" not in st.session_state:
    st.session_state.budget_data = fetch_data_from_sheet()

if "show_briefing" not in st.session_state:
    st.session_state.show_briefing = False

# UI 타이틀
st.markdown(
    "<h1 style='text-align: center;'>📊 팀 예산 관리 시스템</h1>",
    unsafe_allow_html=True,
)
st.markdown("---")

# ==================== [상부 브리핑 버튼 영역] ====================
top_col1, top_col2, top_col3 = st.columns([1, 2, 1])
with top_col2:
    if st.button(
        "🤖 AI 예산 집계 및 분석 브리핑 보기",
        use_container_width=True,
        type="primary",
    ):
        # 클릭할 때마다 최신 데이터를 가져옴
        st.session_state.budget_data = fetch_data_from_sheet()
        st.session_state.show_briefing = not st.session_state.show_briefing

# 브리핑 토글 표시 영역
if st.session_state.show_briefing:
    df_current = pd.DataFrame(st.session_state.budget_data)
    briefing_text = generate_budget_report(df_current)

    with st.expander("📌 예산 집계 분석 리포트 (클릭하여 접기)", expanded=True):
        st.info(briefing_text)

st.markdown("---")
# ===================================================================

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
            month = st.text_input("해당 월 (YYYY-MM)", value=current_month)
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

                    with st.spinner("구글 시트에 저장 중..."):
                        success, err_msg = insert_data_to_sheet(new_entry)

                    if success:
                        st.success("성공적으로 저장되었습니다!")
                        st.session_state.budget_data = fetch_data_from_sheet()
                        st.rerun()
                    else:
                        st.error(f"저장 실패: {err_msg}")
                else:
                    st.warning("월과 금액을 바르게 입력해 주세요.")

    with col2:
        col_title, col_refresh = st.columns([4, 1])
        with col_title:
            st.subheader("📂 최근 입력 내역")
        with col_refresh:
            if st.button("🔄 새로고침"):
                st.session_state.budget_data = fetch_data_from_sheet()
                st.rerun()

        if st.session_state.budget_data:
            df_history = pd.DataFrame(st.session_state.budget_data)

            for idx, row in df_history.iloc[::-1].iterrows():
                c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 3, 1])
                c1.write(str(row.get("날짜", "")))
                c2.write(str(row.get("팀원", "")))
                c3.markdown(f"**{row.get('항목', '')}**")

                try:
                    amt_val = int(float(row.get("금액", 0)))
                except Exception:
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
        st.warning("표시할 데이터가 없습니다.")
    else:
        df_all = pd.DataFrame(st.session_state.budget_data)
        df_all["금액"] = pd.to_numeric(df_all["금액"], errors="coerce").fillna(0)

        total_sum = df_all["금액"].sum()
        total_count = len(df_all)

        m1, m2 = st.columns(2)
        m1.metric("전체 누적 사용액", f"{total_sum:,.0f}원")
        m2.metric("데이터 건수", f"{total_count}건")

        st.markdown("---")
        st.dataframe(df_all, use_container_width=True)
