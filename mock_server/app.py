import warnings

# Suppress FutureWarnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from flask import Flask, request, jsonify
from transformers import AutoFeatureExtractor, AutoModelForImageClassification
from PIL import Image
import torch
import io
import time
import os
from health_check import add_health_endpoint

app = Flask(__name__)

# 건강 체크 엔드포인트 추가
add_health_endpoint(app)

MODEL_NAME = os.environ.get("MODEL_NAME", "google/vit-base-patch16-224")

print(f"모델 로딩 시작: {MODEL_NAME}")
extractor = AutoFeatureExtractor.from_pretrained(MODEL_NAME)
model = AutoModelForImageClassification.from_pretrained(MODEL_NAME)
print("모델 로딩 완료")

# 디바이스 설정 (GPU 사용 가능 시)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"사용 중인 디바이스: {device}")
model.to(device)
model.eval()

@app.route("/analyze", methods=["POST"], strict_slashes=False)
def analyze_image():
    start_time = time.time()

    if "file" not in request.files:
        print("파일이 없습니다!")  # 🔥 디버그용 출력
        return jsonify({"status": "error", "message": "No file uploaded"}), 400

    file = request.files["file"]
    print(f"업로드된 파일 이름: {file.filename}")  # 🔥 디버그용 출력

    try:
        image = Image.open(io.BytesIO(file.read())).convert("RGB")
    except Exception as e:
        print(f"이미지 열기 실패: {e}")  # 🔥 디버그용 출력
        return jsonify({"status": "error", "message": "Failed to process image"}), 400

    inputs = extractor(images=image, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=1)
        pred_class_idx = probs.argmax(dim=1).item()
        confidence = probs[0, pred_class_idx].item()
        print(f"confidence: {confidence}")
    predicted_label = model.config.id2label[pred_class_idx]

    # 결과 생성
    abnormality_score = int(confidence * 100)
    flags = [predicted_label.lower()]

    response = {
        "status": "success",
        "model_type": "huggingface",
        "processing_time_ms": round((time.time() - start_time) * 1000, 2),
        "result": {
            "abnormality_score": abnormality_score,
            "confidence": confidence,
            "flags": flags
        }
    }

    return jsonify(response), 200

@app.route("/analyze/error", methods=["POST"], strict_slashes=False)
def simulate_error():
    """
    오류 시뮬레이션 엔드포인트
    테스트에서 오류 처리를 확인하기 위해 사용됩니다.
    """
    return jsonify({
        "status": "error",
        "message": "Internal server error simulation",
        "error_code": "INTERNAL_ERROR"
    }), 500

@app.route("/analyze/metadata", methods=["GET"], strict_slashes=False)
def get_model_metadata():
    """
    모델 메타데이터 제공 엔드포인트
    FDA와 ISO13485 규제 요구사항을 충족하기 위한 정보를 제공합니다.
    """
    return jsonify({
        "version": "1.0.0",
        "regulatory_status": "FDA cleared",
        "intended_use": "Chest X-ray abnormality detection",
        "sensitivity": 0.95,
        "specificity": 0.92,
        "last_updated": "2024-05-01",
        "model_id": "lunit-care-qa-v1",
        "model_type": "huggingface",
        "base_model": MODEL_NAME
    }), 200

@app.route("/", methods=["GET"], strict_slashes=False)
def index():
    """
    기본 엔드포인트
    서버가 실행 중임을 나타내는 기본 응답입니다.
    """
    return jsonify({
        "service": "LunitCare QA Mock API Server",
        "version": os.environ.get("SERVICE_VERSION", "development"),
        "endpoints": ["/analyze", "/health", "/analyze/error", "/analyze/metadata"]
    }), 200

# 이렇게 하면 /analyze 대신 더 가벼운 API로 확인 가능:
@app.route("/healthz")
def health_check():
    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    debug = os.environ.get("DEBUG", "False").lower() == "true"
    
    print(f"서버 시작: {host}:{port} (디버그: {debug})")
    app.run(host=host, port=port, debug=debug)