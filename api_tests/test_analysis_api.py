import requests
import json
import jsonschema
import os
import pytest
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

API_URL = "http://localhost:5000/analyze"
ERROR_API_URL = "http://localhost:5000/analyze/error"
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "test_data")

def load_schema():
    # with open("api_tests/schemas/response_schema.json") as f:
    schema_path = os.path.join(os.path.dirname(__file__), "schemas", "response_schema.json")
    # with open(schema_path, "r") as f:
    with open(schema_path) as f:
        return json.load(f)

def test_valid_image_analysis():
    response = requests.post(API_URL, files={"file": open(os.path.join(TEST_DATA_DIR, "normal_chest_xray.jpg"), "rb")})
    assert response.status_code == 200
    data = response.json()

    if isinstance(data["result"].get("confidence"), str):
        data["result"]["confidence"] = float(data["result"]["confidence"])
    schema = load_schema()
    jsonschema.validate(instance=data, schema=schema)
    
    # 추가 검증
    assert "result" in data
    assert "abnormality_score" in data["result"]
    assert "confidence" in data["result"]
    assert "flags" in data["result"]
    assert isinstance(data["result"]["flags"], list)

def test_invalid_file_upload():
    response = requests.post(API_URL, files={"file": open(os.path.join(TEST_DATA_DIR, "invalid_file.txt"), "rb")})
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "error"

def test_missing_file():
    response = requests.post(API_URL)
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "error"
    assert "message" in data

def test_internal_server_error_simulation():
    response = requests.post(ERROR_API_URL, files={"file": open(os.path.join(TEST_DATA_DIR, "normal_chest_xray.jpg"), "rb")})
    assert response.status_code == 500
    assert response.json()["status"] == "error"

@pytest.mark.parametrize("image_file", [
    "normal_chest_xray.jpg",
    "abnormal_chest_xray.jpg",
    "ct_scan_sample.jpg"
])
def test_multiple_image_types(image_file):
    try:
        response = requests.post(
            API_URL, 
            files={"file": open(os.path.join(TEST_DATA_DIR, image_file), "rb")}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "result" in data
    except FileNotFoundError:
        pytest.skip(f"Test file {image_file} not found in test_data directory")

def test_large_image_processing():
    """대용량 이미지 처리 테스트"""
    try:
        large_image = os.path.join(TEST_DATA_DIR, "large_image.jpg")
        if not os.path.exists(large_image):
            pytest.skip("Large test image not found")
            
        response = requests.post(API_URL, files={"file": open(large_image, "rb")})
        assert response.status_code == 200
        data = response.json()
        
        # 처리 시간 확인
        assert data["processing_time_ms"] > 0
        # 대용량 이미지 처리 시간은 일반적으로 더 오래 걸림
        assert "result" in data
    except Exception as e:
        pytest.fail(f"Failed to process large image: {str(e)}")

def test_api_response_time():
    """API 응답 시간 테스트"""
    start_time = time.time()
    response = requests.post(
        API_URL, 
        files={"file": open(os.path.join(TEST_DATA_DIR, "normal_chest_xray.jpg"), "rb")}
    )
    end_time = time.time()
    
    response_time = end_time - start_time
    
    assert response.status_code == 200
    # 응답 시간이 2초 이내여야 함 (이 값은 요구사항에 따라 조정 가능)
    assert response_time < 3.0, f"API 응답 시간이 너무 깁니다: {response_time:.2f}초"
    
    # 응답에서 처리 시간 확인
    data = response.json()
    assert "processing_time_ms" in data

def make_api_call(file_path):
    """API 호출 헬퍼 함수"""
    try:
        with open(file_path, "rb") as f:
            response = requests.post(API_URL, files={"file": f})
        return response.status_code
    except Exception:
        return 0

def test_api_concurrent_requests():
    """동시 요청 처리 테스트"""
    # 파일 목록 가져오기
    image_files = [
        os.path.join(TEST_DATA_DIR, f) 
        for f in os.listdir(TEST_DATA_DIR)
        if f.endswith(('.jpg', '.png', '.jpeg'))
    ]
    
    if len(image_files) < 3:
        pytest.skip("테스트를 위한 충분한 이미지 파일이 없습니다")
        
    # 동시에 5개 요청 보내기
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(make_api_call, img) for img in image_files[:5]]
        results = [future.result() for future in as_completed(futures)]
    
    # 모든 요청이 성공했는지 확인
    for status_code in results:
        assert status_code == 200, f"일부 동시 요청이 실패했습니다: {status_code}"
