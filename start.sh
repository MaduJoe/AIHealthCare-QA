#!/bin/bash
set -e

# 시작 메시지
echo "LunitCare QA 시스템을 시작합니다..."

# 백그라운드에서 Mock API 서버 시작
echo "Mock API 서버를 시작합니다..."
# cd /app/mock_server
python mock_server/app.py &
MOCK_SERVER_PID=$!

# 서버가 시작될 때까지 잠시 대기
sleep 2

# Streamlit UI 서버 시작
echo "Streamlit UI를 시작합니다..."
# cd /app
streamlit run ui_app.py &
UI_SERVER_PID=$!

# 모든 프로세스가 종료되기를 기다림
wait $MOCK_SERVER_PID $UI_SERVER_PID 