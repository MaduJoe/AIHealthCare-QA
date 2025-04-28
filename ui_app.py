import streamlit as st
import requests
import json
from PIL import Image
import io
import base64
import pandas as pd
import time
import random
import re
import os
from datetime import datetime

# API 설정
API_URL = os.getenv("API_URL", "http://localhost:5000")
API_KEY = os.getenv("API_KEY", "test_api_key")
HEADERS = {"X-API-Key": API_KEY}

# 세션 상태 초기화
# for key in ['logs', 'ui_refresh_counter', 'show_patient_form', 'show_logs', 
#             'log_container', 'patients', 'patient_id', 'patient_name', 'patient_birthdate']:
#     if key not in st.session_state:
#         st.session_state[key] = [] if key == 'logs' else 0 if key == 'ui_refresh_counter' else False if 'show_' in key else ""


for key in ['logs', 'ui_refresh_counter', 'show_patient_form', 'show_logs', 
            'log_container', 'patients', 'patient_id', 'patient_name', 'patient_birthdate']:
    if key not in st.session_state:
        if key in ['logs', 'patients']:
            st.session_state[key] = []
        elif key == 'ui_refresh_counter':
            st.session_state[key] = 0
        elif 'show_' in key:
            st.session_state[key] = False
        else:
            st.session_state[key] = ""


# 로그 추가 함수
def add_log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.logs.append(f"[{timestamp}] {message}")
    if len(st.session_state.logs) > 100:
        st.session_state.logs = st.session_state.logs[-100:]

# 분석 API 호출 함수
def analyze_image(image_bytes, filename):
    add_log("사용자가 AI 판독 요청함")
    try:
        response = requests.post(
            f"{API_URL}/analyze",
            headers=HEADERS,
            files={"file": (filename, image_bytes, "image/jpeg")}
        )
        if response.status_code == 200:
            result = response.json()
            st.session_state.analysis_result = result
            st.session_state.analyzed_image = image_bytes
            st.session_state.analysis_timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            add_log(f"분석 완료: 비정상 점수 {result['result']['abnormality_score']}")
            return True
        else:
            add_log(f"API 오류: {response.status_code}")
            return False
    except Exception as e:
        add_log(f"분석 오류 발생: {str(e)}")
        return False

# 환자 등록 함수
def register_patient(patient_id, patient_name, birthdate):
    if not (patient_id and patient_name):
        add_log("환자 등록 실패: 필수 정보 누락")
        return False
    add_log(f"사용자가 환자 등록: ID={patient_id}, 이름={patient_name}")
    patient_data = {
        "id": patient_id,
        "name": patient_name,
        "birthdate": birthdate,
        "timestamp": datetime.now().isoformat()
    }
    if 'analysis_result' in st.session_state:
        patient_data["analysis_result"] = st.session_state.analysis_result
    st.session_state.patients.append(patient_data)
    st.session_state.show_patient_form = False
    return True


# 페이지 기본 설정
st.set_page_config(
    page_title="LunitCare - AI 의료 영상 분석",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 의료 용어 간단 설명 매핑
medical_terms = {
    "nodule": "폐 결절(멍울)",
    "opacity": "폐 음영(흰 부분)",
    "mass": "종괴(덩어리)",
    "consolidation": "폐 경화",
    "effusion": "흉수",
    "pneumothorax": "기흉"
}

# 메인 제목
st.markdown("<h1 style='text-align: center; color: #2C3E50;'>LunitCare AI 의료 영상 분석</h1>", unsafe_allow_html=True)

# 탭 구성
tabs = st.tabs(["📊 이미지 분석", "📋 결과 히스토리", "ℹ️ 시스템 정보"])

with tabs[0]:  # 📊 이미지 분석 탭
    upload_col, result_col = st.columns([1, 1.5])

    with upload_col:
        st.subheader("🖼️ 이미지 업로드")
        uploaded_file = st.file_uploader("JPG, JPEG, PNG, DICOM 업로드", type=["jpg", "jpeg", "png", "dcm", "dicom"])
        
        if uploaded_file is not None:
            add_log(f"사용자가 이미지 파일 업로드: {uploaded_file.name}")
            image = Image.open(uploaded_file)
            st.image(image, caption="업로드된 이미지", use_container_width=True)

            if st.button("AI 판독 요청", use_container_width=True, type="primary"):
                with st.spinner("AI가 이미지를 분석 중입니다..."):
                    uploaded_file.seek(0)
                    file_bytes = uploaded_file.getvalue()
                    success = analyze_image(file_bytes, uploaded_file.name)
                    if success:
                        st.success("AI 분석 완료!")
                    else:
                        st.error("분석 실패. 다시 시도해주세요.")

    with result_col:
        if 'analysis_result' in st.session_state:
            result = st.session_state.analysis_result
            abnormality_score = result["result"]["abnormality_score"]

            with st.container(border=True):
                st.subheader("🔍 발견된 소견")
                if len(result["result"]["flags"]) > 0:
                    for flag in result["result"]["flags"]:
                        friendly_term = medical_terms.get(flag, flag)
                        st.info(f"🔵 {friendly_term}")
                else:
                    st.success("특이 소견이 발견되지 않았습니다.")

                st.metric(label="비정상 점수", value=f"{abnormality_score}%", delta_color="inverse")

                st.subheader("🩺 치료 적합성 평가")
                if abnormality_score > 50:
                    st.success("🟢 면역치료 적합")
                else:
                    st.error("🔴 면역치료 부적합")


            st.divider()

            st.subheader("📝 환자 등록")
            with st.form(key="patient_form"):
                patient_id = st.text_input("환자 ID", value=st.session_state.get("patient_id", ""), placeholder="예: PT-0001")
                patient_name = st.text_input("환자 이름", value=st.session_state.get("patient_name", ""), placeholder="예: 홍길동")
                birthdate = st.text_input("생년월일", value=st.session_state.get("patient_birthdate", ""), placeholder="예: 1990-01-01")
                
                submit_button = st.form_submit_button(label="등록 완료")
                if submit_button:
                    if patient_id and patient_name:
                        register_patient(patient_id, patient_name, birthdate)
                        st.success("환자 등록이 완료되었습니다!")

                        # 입력창 초기화
                        st.session_state.patient_id = ""
                        st.session_state.patient_name = ""
                        st.session_state.patient_birthdate = ""
                    else:
                        st.error("환자 ID와 이름은 필수 입력 항목입니다.")

            if st.session_state.patients:
                st.subheader("👥 등록된 환자 목록")
                patients_df = pd.DataFrame(st.session_state.patients)
                st.dataframe(patients_df, use_container_width=True)

            st.divider()

            st.subheader("✉️ 분석 결과 이메일 전송 (시뮬레이션)")
            email = st.text_input("이메일 주소 입력", placeholder="example@email.com")
            send_email_button = st.button("분석 결과 전송")
            if send_email_button:
                if re.match(r"[^@]+@[^@]+\.[^@]+", email):
                    st.success(f"분석 결과가 {email}로 전송되었습니다! (시뮬레이션)")
                    add_log(f"분석 결과 이메일 전송됨: {email}")
                else:
                    st.error("유효한 이메일 주소를 입력하세요.")

            st.divider()

            def generate_report_text():
                result = st.session_state.analysis_result["result"]
                abnormality_score = result["abnormality_score"]
                flags = result["flags"]
                flag_list = ", ".join(flags) if flags else "특이 소견 없음"
                patient_id = st.session_state.get("patient_id", "N/A")
                patient_name = st.session_state.get("patient_name", "N/A")
                birthdate = st.session_state.get("patient_birthdate", "N/A")
                evaluation = "면역치료 적합" if abnormality_score > 50 else "면역치료 부적합"

                report_text = f"""
LunitCare AI 분석 결과 보고서
-----------------------------

🗓️ 분석 날짜: {time.strftime("%Y-%m-%d")}
👤 환자 ID: {patient_id}
👤 환자 이름: {patient_name}
📅 생년월일: {birthdate}

🔎 분석 결과
- 비정상 점수: {abnormality_score}%
- 발견된 소견: {flag_list}

🩺 치료 적합성 평가
- 결과: {evaluation}
                """
                return report_text.strip()

            report_text = generate_report_text()
            st.download_button(
                label="📄 결과 저장 (PDF)",
                data=report_text,
                file_name=f"AI_분석결과_{time.strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=False
            )

with tabs[1]:  # 📋 결과 히스토리 탭
    st.subheader("분석 히스토리 (예시 데이터)")
    data = {
        "환자 ID": ["PT-1001", "PT-1002", "PT-1003", "PT-1004", "PT-1005"],
        "검사 유형": ["X-Ray", "CT", "X-Ray", "MRI", "CT"],
        "분석 날짜": ["2025-04-15", "2025-04-16", "2025-04-17", "2025-04-18", "2025-04-19"],
        "비정상 점수": [75.3, 12.1, 92.7, 45.6, 8.3],
        "진단": ["폐 결절", "정상", "폐렴 의심", "요추 디스크", "정상"]
    }
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)

with tabs[2]:  # ℹ️ 시스템 정보 탭
    st.subheader("LunitCare AI 시스템 정보 (샘플)")
    st.info("버전: 1.3.0\n모델: Google ViT\n분석 엔진: HuggingFace Transformers 기반\n주요 기능: 의료 영상 AI 진단 보조")
