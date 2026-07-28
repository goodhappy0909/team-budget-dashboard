import gspread
import pandas as pd
import streamlit as st

# 스트림릿 페이지 설정
st.title("구글 스프레드시트 연동 Streamlit 앱")


# 캐시를 사용하여 데이터를 불러옴 (성능 최적화)
@st.cache_data(ttl=600)  # 10분마다 캐시 갱신
def load_data():
  # 1. 서비스 계정 인증 정보 로드 (Streamlit secrets 또는 로컬 파일 사용)
  # 로컬 테스트 시: 'credentials.json' 파일 경로 사용
  gc = gspread.service_account(filename="credentials.json")

  # 2. 스프레드시트 문서 및 시트 선택
  spreadsheet_url = (
      "여기에_구글_스프레드시트_URL을_입력하세요"  # 또는 스프레드시트 이름
  )
  sh = gc.open_by_url(spreadsheet_url)
  worksheet = sh.get_worksheet(0)  # 첫 번째 시트 선택

  # 3. 데이터를 DataFrame으로 변환
  data = worksheet.get_all_records()
  df = pd.DataFrame(data)
  return df


try:
  df = load_data()

  # 데이터 출력
  st.subheader("스프레드시트 원본 데이터")
  st.dataframe(df)

  # 간단한 데이터 분석 또는 시각화 예시
  st.subheader("데이터 통계 요약")
  st.write(df.describe())

except Exception as e:
  st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
