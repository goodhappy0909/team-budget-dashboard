import pandas as pd
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="팀 예산 관리 대시보드", page_icon="💰", layout="wide"
)

# 타이틀
st.title("💰 팀 예산 관리 대시보드")
st.markdown("팀의 예산 사용 현황을 실시간으로 확인하고 관리하세요.")

# 예시 데이터 생성 (실제 데이터프레임이나 CSV 파일로 대체 가능)
if "budget_data" not in st.session_state:
    st.session_state.budget_data = pd.DataFrame(
    {
        "항목": ["회식비", "도서구입", "소프트웨어 구독", "간식비", "출장비"],
        "카테고리": [
            "복리후생",
            "자기계발",
            "도구/인프라",
            "복리후생",
            "업무출장",
        ],
        "배정예산": [1000000, 500000, 2000000, 300000, 1500000],
        "사용금액": [750000, 200000, 2000000, 250000, 800000],
    }
)

df = st.session_state.budget_data
df["잔액"] = df["배정예산"] - df["사용금액"]
df["사용률(%)"] = (df["사용금액"] / df["배정예산"] * 100).round(1)

# 상단 주요 지표 (Metrics)
total_budget = df["배정예산"].sum()
total_used = df["사용금액"].sum()
total_remain = df["잔액"].sum()

col1, col2, col3 = st.columns(3)
col1.metric("총 배정 예산", f"{total_budget:,.0f} 원")
col2.metric("총 사용 금액", f"{total_used:,.0f} 원")
col3.metric("남은 예산", f"{total_remain:,.0f} 원")

st.markdown("---")

# 예산 항목별 현황 테이블
st.subheader("📊 항목별 예산 상세 현황")
st.dataframe(df, use_container_width=True)

# 지출 내역 추가 섹션
st.markdown("---")
st.subheader("➕ 새로운 지출 내역 추가")

with st.form("expense_form"):
    col_a, col_b = st.columns(2)
    with col_a:
        item_name = st.text_input("항목 이름")
        item_category = st.selectbox(
            "카테고리", ["복리후생", "자기계발", "도구/인프라", "업무출장", "기타"]
        )
    with col_b:
        allocated = st.number_input("배정 예산 (원)", min_value=0, step=10000)
        used = st.number_input("사용 금액 (원)", min_value=0, step=10000)

    submitted = st.form_submit_button("추가하기")
    if submitted:
        if item_name:
            new_row = pd.DataFrame(
                {
                    "항목": [item_name],
                    "카테고리": [item_category],
                    "배정예산": [allocated],
                    "사용금액": [used],
                }
            )
            st.session_name = pd.concat(
                [st.session_state.budget_data, new_row], ignore_index=True
            )
            st.success(f"'{item_name}' 항목이 추가되었습니다!")
            st.rerun()
        else:
            st.warning("항목 이름을 입력해주세요.")
