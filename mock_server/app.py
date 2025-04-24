from flask import Flask, request, jsonify
import os
import random
import time


app = Flask(__name__)

# 의료 AI 시스템 시뮬레이션을 위한 지연 설정 (실제 AI 분석 시간 시뮬레이션)
MIN_PROCESSING_DELAY = 0.5  # 초 단위
MAX_PROCESSING_DELAY = 2.0  # 초 단위

# 유효한 이미지 형식 목록
VALID_IMAGE_TYPES = ['jpeg', 'jpg', 'png', 'bmp']

# 병변 유형 목록 (의료 영상 분석 결과 시뮬레이션)
ABNORMALITY_TYPES = ['nodule', 'opacity', 'mass', 'consolidation', 'effusion', 'pneumothorax']

@app.route("/analyze", methods=["POST"])
def analyze():
    # 요청에 이미지가 없는 경우
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400
    
    image_file = request.files["image"]
    
    # 파일명이 비어있는 경우
    if image_file.filename == '':
        return jsonify({"error": "Empty filename"}), 400
    
    # 파일 크기 확인 (너무 큰 파일 거부, 15MB 제한)
    if len(image_file.read()) > 15 * 1024 * 1024:
        return jsonify({"error": "Image too large (max 15MB)"}), 400
    
    # AI 처리 시간 시뮬레이션
    processing_time = random.uniform(MIN_PROCESSING_DELAY, MAX_PROCESSING_DELAY)
    time.sleep(processing_time)
    
    # 파일명에 따라 다른 결과 생성 (테스트 목적)
    filename_lower = image_file.filename.lower()
    
    if "normal" in filename_lower:
        # 정상 이미지 시뮬레이션
        abnormality_score = random.uniform(0.5, 25.0)
        flags = []
        if random.random() < 0.2:  # 20% 확률로 낮은 점수 플래그 추가
            flags.append(random.choice(ABNORMALITY_TYPES))
    else:
        # 비정상 이미지 시뮬레이션
        abnormality_score = random.uniform(60.0, 98.0)
        # 1~3개의 무작위 병변 플래그 선택
        flags = random.sample(ABNORMALITY_TYPES, random.randint(1, 3))
    
    return jsonify({
        "status": "success",
        "result": {
            "abnormality_score": round(abnormality_score, 1),
            "flags": flags,
            "processing_time_ms": round(processing_time * 1000)
        }
    }), 200

@app.route("/analyze/metadata", methods=["GET"])
def get_metadata():
    """의료기기 규제 관련 메타데이터 제공 엔드포인트"""
    return jsonify({
        "version": "1.2.3",
        "model_id": "LunitCare-Chest-XRay-v2",
        "last_updated": "2023-07-15",
        "regulatory_status": "FDA cleared",
        "intended_use": "보조적 진단 도구 (CADx)",
        "sensitivity": 0.92,
        "specificity": 0.89,
        "supported_modalities": ["X-Ray", "CT"],
        "training_dataset": "Anonymized chest X-rays from multiple institutions",
        "algorithm_type": "Deep Learning CNN"
    }), 200

# 오류 시뮬레이션 엔드포인트 (의도적 서버 오류 시뮬레이션)
@app.route("/analyze/error", methods=["POST"])
def simulate_error():
    """테스트 목적으로 다양한 오류 상황을 시뮬레이션"""
    error_type = request.args.get("type", "server_error")
    
    if error_type == "timeout":
        time.sleep(30)  # 30초 타임아웃
        return jsonify({"error": "Request timed out"}), 408
    
    elif error_type == "overloaded":
        return jsonify({"error": "Server is currently overloaded"}), 503
    
    elif error_type == "maintenance":
        return jsonify({"error": "System is under maintenance"}), 503
    
    else:  # 기본 서버 오류
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(debug=True)
