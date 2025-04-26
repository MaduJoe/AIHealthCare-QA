from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/analyze", methods=["POST"])
def analyze():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400

    return jsonify({
        "status": "success",
        "result": {
            "abnormality_score": 92.7,
            "flags": ["nodule", "opacity"]
        }
    }), 200

@app.route("/analyze/error", methods=["POST"])
def analyze_error():
    return jsonify({
        "status": "error",
        "message": "Internal server error simulated for testing"
    }), 500

@app.route("/analyze/metadata", methods=["GET"])
def metadata():
    return jsonify({
        "version": "1.2.0",
        "model_id": "LUNG-CT-V2",
        "last_updated": "2023-09-01",
        "regulatory_status": "연구용(Research Use Only)",
        "intended_use": "폐 질환 판독 보조",
        "supported_modalities": ["X-Ray", "CT"],
        "sensitivity": 0.92,
        "specificity": 0.89
    })

if __name__ == "__main__":
    app.run(debug=True)
