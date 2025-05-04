"""
LunitCare QA Mock 서버 건강 체크 엔드포인트
Docker 환경에서 컨테이너 상태 확인용으로 사용됩니다.
"""

from flask import Flask, jsonify
import time
import os

# 기존 app.py에 추가하는 대신 별도 파일로 생성
# 실제 사용 시에는 app.py에 이 코드를 통합해야 합니다

def add_health_endpoint(app):
    """
    Flask 앱에 건강 체크 엔드포인트를 추가합니다.
    """
    
    @app.route("/health", methods=["GET"])
    def health_check():
        """
        서버 상태를 확인하는 엔드포인트
        Docker 컨테이너의 헬스체크에 사용됩니다.
        """
        return jsonify({
            "status": "ok",
            "timestamp": time.time(),
            "service": "lunitcare-mock-api",
            "version": os.environ.get("SERVICE_VERSION", "development")
        }), 200

if __name__ == "__main__":
    # 단독 실행 시 테스트용 서버 시작
    app = Flask(__name__)
    add_health_endpoint(app)
    app.run(host="0.0.0.0", port=5000) 