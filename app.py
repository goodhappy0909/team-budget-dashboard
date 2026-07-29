import json
import requests
import streamlit as st


def insert_data_to_sheet(entry):
    """구글 시트에 새로운 데이터 추가 (GET Query String 방식)"""
    try:
        # JSON 객체를 문자열로 변환하여 쿼리 파라미터로 전달
        payload_data = json.dumps(
            {
                "id": str(entry["id"]),
                "날짜": str(entry["날짜"]),
                "팀원": str(entry["팀원"]),
                "항목": str(entry["항목"]),
                "금액": int(entry["금액"]),
            }
        )

        params = {"action": "insert", "data": payload_data}

        # requests.get을 사용하여 URL 파라미터로 전송
        response = requests.get(
            GAS_WEB_APP_URL, params=params, timeout=10, allow_redirects=True
        )
        result = response.json()

        if result.get("status") == "success":
            return True, ""
        else:
            return False, result.get("message", "알 수 없는 서버 에러")
    except Exception as e:
        return False, str(e)


def delete_data_from_sheet(row_id):
    """구글 시트에서 특정 데이터 삭제 (GET Query String 방식)"""
    try:
        params = {
            "action": "delete",
            "idColumn": "id",
            "idValue": str(row_id),
        }
        response = requests.get(
            GAS_WEB_APP_URL, params=params, timeout=10, allow_redirects=True
        )
        result = response.json()
        return result.get("status") == "success"
    except Exception as e:
        st.error(f"데이터 삭제 중 오류 발생: {e}")
        return False
