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

if __name__ == "__main__":
    app.run(debug=True)
