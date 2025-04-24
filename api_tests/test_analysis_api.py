import requests
import jsonschema
import pytest
import os
import time
from pathlib import Path

API_URL = "http://localhost:5000/analyze"
TEST_DATA_DIR = Path(__file__).parent / "test_data"

# 테스트 데이터가 없을 경우를 대비한 픽스처
@pytest.fixture(scope="session")
def sample_images():
    # 테스트 데이터 디렉토리 생성
    os.makedirs(TEST_DATA_DIR, exist_ok=True)
    
    # 현재는 단순 예시이지만, 실제로는 다양한 의료 영상 데이터셋 구성 필요
    samples = {
        "normal": TEST_DATA_DIR / "normal_chest_xray.jpg",
        "abnormal": TEST_DATA_DIR / "abnormal_chest_xray.jpg",
        "invalid": TEST_DATA_DIR / "invalid_file.txt",
        "large": TEST_DATA_DIR / "large_image.jpg",
    }
    
    # 파일이 이미 존재하는지 확인
    for img_type, path in samples.items():
        if not path.exists():
            print(f"Warning: Test image {path} does not exist. Some tests may fail.")
    
    return samples

# 기본 응답 스키마 검증
def validate_analysis_schema(data):
    schema = {
        "type": "object",
        "properties": {
            "status": {"type": "string"},
            "result": {
                "type": "object",
                "properties": {
                    "abnormality_score": {"type": "number"},
                    "flags": {"type": "array"},
                },
                "required": ["abnormality_score", "flags"]
            }
        },
        "required": ["status", "result"]
    }
    jsonschema.validate(instance=data, schema=schema)

# 정상 이미지 분석 테스트
def test_valid_image_analysis(sample_images):
    if not sample_images["normal"].exists():
        pytest.skip("테스트 이미지 파일이 없습니다.")
        
    response = requests.post(API_URL, files={"image": open(sample_images["normal"], "rb")})
    assert response.status_code == 200
    data = response.json()
    
    validate_analysis_schema(data)
    
    # 정상 이미지는 낮은 비정상 점수를 가져야 함
    abnormality_score = data["result"]["abnormality_score"]
    assert abnormality_score <= 30.0, f"정상 이미지의 비정상 점수가 너무 높습니다: {abnormality_score}"

# 비정상 이미지 분석 테스트
def test_abnormal_image_analysis(sample_images):
    if not sample_images["abnormal"].exists():
        pytest.skip("테스트 이미지 파일이 없습니다.")
        
    response = requests.post(API_URL, files={"image": open(sample_images["abnormal"], "rb")})
    assert response.status_code == 200
    data = response.json()
    
    validate_analysis_schema(data)
    
    # 비정상 이미지는 높은 비정상 점수를 가져야 함
    abnormality_score = data["result"]["abnormality_score"]
    assert abnormality_score > 50.0, f"비정상 이미지의 비정상 점수가 너무 낮습니다: {abnormality_score}"
    
    # 하나 이상의 플래그가 있어야 함
    assert len(data["result"]["flags"]) > 0, "비정상 이미지는 하나 이상의 플래그를 가져야 합니다"

# 이미지 없는 요청 테스트
def test_missing_image():
    response = requests.post(API_URL)
    assert response.status_code == 400
    data = response.json()
    assert "error" in data

# 잘못된 파일 형식 테스트
def test_invalid_file_format(sample_images):
    if not sample_images["invalid"].exists():
        pytest.skip("테스트 이미지 파일이 없습니다.")
        
    response = requests.post(API_URL, files={"image": open(sample_images["invalid"], "rb")})
    assert response.status_code == 400
    data = response.json()
    assert "error" in data

# 대용량 이미지 테스트
def test_large_image_handling(sample_images):
    if not sample_images["large"].exists():
        pytest.skip("테스트 이미지 파일이 없습니다.")
        
    response = requests.post(API_URL, files={"image": open(sample_images["large"], "rb")})
    # 대용량 이미지도 처리할 수 있어야 함 (시간이 좀 더 걸릴 수 있음)
    assert response.status_code == 200

# 응답 시간 테스트 (성능 테스트)
def test_response_time(sample_images):
    if not sample_images["normal"].exists():
        pytest.skip("테스트 이미지 파일이 없습니다.")
        
    start_time = time.time()
    response = requests.post(API_URL, files={"image": open(sample_images["normal"], "rb")})
    end_time = time.time()
    
    # 응답 시간이 5초 이내여야 함 (실제 요구사항에 따라 조정)
    assert end_time - start_time < 5.0, f"응답 시간이 너무 깁니다: {end_time - start_time:.2f}초"
    assert response.status_code == 200

# 의료 AI 특화 메타데이터 테스트
def test_medical_metadata():
    response = requests.get(f"{API_URL}/metadata")
    assert response.status_code == 200
    data = response.json()
    
    # 의료기기 규제에 필요한 메타데이터 검증
    required_fields = ["version", "model_id", "last_updated", "regulatory_status"]
    for field in required_fields:
        assert field in data, f"필수 메타데이터 필드가 누락되었습니다: {field}"

# 연속적인 요청 테스트 (안정성 테스트)
def test_consecutive_requests(sample_images):
    if not sample_images["normal"].exists():
        pytest.skip("테스트 이미지 파일이 없습니다.")
        
    # 연속 10회 요청 테스트
    for i in range(10):
        response = requests.post(API_URL, files={"image": open(sample_images["normal"], "rb")})
        assert response.status_code == 200, f"{i+1}번째 연속 요청이 실패했습니다."
