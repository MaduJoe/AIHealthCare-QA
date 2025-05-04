# LunitCare QA 시스템 Docker 이미지
FROM python:3.9-slim

WORKDIR /app

# 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# 애플리케이션 소스 복사
COPY . /app/

# 파이썬 요구사항 설치
RUN pip3 install --no-cache-dir -r requirements.txt

# Mock 서버 포트 및 Streamlit UI 포트 노출
EXPOSE 5000 8501

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1

# 시작 스크립트 복사 및 실행 권한 부여
COPY start.sh /app/
RUN chmod +x /app/start.sh

# 컨테이너 시작 시 실행되는 명령
CMD ["/app/start.sh"] 