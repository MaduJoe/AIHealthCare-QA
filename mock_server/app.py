from flask import Flask, request, jsonify
from transformers import AutoFeatureExtractor, AutoModelForImageClassification
from PIL import Image
import torch
import io
import time

app = Flask(__name__)

MODEL_NAME = "google/vit-base-patch16-224"

extractor = AutoFeatureExtractor.from_pretrained(MODEL_NAME)
model = AutoModelForImageClassification.from_pretrained(MODEL_NAME)

# 디바이스 설정 (GPU 사용 가능 시)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

@app.route("/analyze", methods=["POST"])
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

    predicted_label = model.config.id2label[pred_class_idx]

    # 결과 생성
    abnormality_score = int(confidence * 100)
    flags = [predicted_label.lower()]

    response = {
        "model_type": "huggingface",
        "processing_time_ms": round((time.time() - start_time) * 1000, 2),
        "result": {
            "abnormality_score": abnormality_score,
            "confidence": f"{confidence:.2f}",
            "flags": flags
        },
        "status": "success"
    }

    return jsonify(response), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
