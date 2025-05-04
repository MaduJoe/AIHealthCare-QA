# LunitCare QA Mock 서버 Docker 이미지
FROM python:3.9-slim

WORKDIR /app

# 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 애플리케이션 소스 복사
COPY . /app/

# 파이썬 요구사항 설치
RUN pip3 install --no-cache-dir -r requirements.txt

# 모델 캐시 디렉토리 생성
RUN mkdir -p /root/.cache/huggingface/

# 포트 노출
EXPOSE 5000

# 건강 체크 엔드포인트 추가
COPY health_check.py /app/

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1
ENV MODEL_NAME=google/vit-base-patch16-224

# 컨테이너 시작 시 실행되는 명령
CMD ["python", "app.py"] 