import requests
import json
import jsonschema

API_URL = "http://localhost:5000/analyze"
ERROR_API_URL = "http://localhost:5000/analyze/error"

def load_schema():
    with open("api_tests/schemas/response_schema.json") as f:
        return json.load(f)

def test_valid_image_analysis():
    response = requests.post(API_URL, files={"image": open("test_data/normal_chest_xray.jpg", "rb")})
    assert response.status_code == 200
    data = response.json()
    schema = load_schema()
    jsonschema.validate(instance=data, schema=schema)

def test_invalid_file_upload():
    response = requests.post(API_URL, files={"image": open("test_data/invalid_file.txt", "rb")})
    assert response.status_code == 400

def test_internal_server_error_simulation():
    response = requests.post(ERROR_API_URL, files={"image": open("test_data/normal_chest_xray.jpg", "rb")})
    assert response.status_code == 500
    assert response.json()["status"] == "error"
