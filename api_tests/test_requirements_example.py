import pytest
import requests
import json
import os
from conftest import req_id

# API 엔드포인트
API_URL = "http://localhost:5000/analyze"
METADATA_URL = "http://localhost:5000/analyze/metadata"

@req_id("REQ-001")
def test_valid_image_upload(api_url, sample_normal_image):
    """
    REQ-001: 이미지를 업로드할 수 있어야 한다
    """
    with open(sample_normal_image, "rb") as img:
        response = requests.post(api_url, files={"file": img})
    
    assert response.status_code == 200
    assert response.json()["status"] == "success"

@req_id("REQ-002")
def test_analysis_completion_message(api_url, sample_abnormal_image):
    """
    REQ-002: 분석 후 'AI 분석 완료!' 메시지가 떠야 한다
    
    참고: 이 테스트는 실제로는 E2E 테스트로 구현해야 하지만,
    여기서는 백엔드 응답을 검증하는 단위 테스트로 대체합니다.
    """
    with open(sample_abnormal_image, "rb") as img:
        response = requests.post(api_url, files={"file": img})
    
    assert response.status_code == 200
    # 실제 UI 테스트에서는 성공 메시지를 확인해야 하지만, 
    # 여기서는 응답 성공 여부로 대체
    assert response.json()["status"] == "success"

@req_id("REQ-003")
def test_api_response_time(api_url, sample_normal_image):
    """
    REQ-003: 분석 응답시간이 평균 2초 이내여야 한다
    """
    import time
    
    start_time = time.time()
    with open(sample_normal_image, "rb") as img:
        response = requests.post(api_url, files={"file": img})
    end_time = time.time()
    
    response_time = end_time - start_time
    assert response.status_code == 200
    
    # 응답 시간이 2초 이내여야 함
    assert response_time < 2.0, f"API 응답 시간이 너무 깁니다: {response_time:.2f}초"

@req_id("REQ-005")
def test_abnormal_detection(api_url, sample_abnormal_image):
    """
    REQ-005: 비정상 영상을 정상적으로 감지해야 한다
    """
    with open(sample_abnormal_image, "rb") as img:
        response = requests.post(api_url, files={"file": img})
    
    assert response.status_code == 200
    result = response.json()["result"]
    
    # 비정상 점수가 50% 이상이어야 함
    assert result["abnormality_score"] > 50, "비정상 이미지를 감지하지 못했습니다"

@req_id("REQ-006")
def test_normal_correct_detection(api_url, sample_normal_image):
    """
    REQ-006: 정상 영상을 비정상으로 잘못 감지하는 비율이 10% 이하여야 한다
    """
    with open(sample_normal_image, "rb") as img:
        response = requests.post(api_url, files={"file": img})
    
    assert response.status_code == 200
    result = response.json()["result"]
    
    # 정상 이미지의 비정상 점수가 30% 이하여야 함
    assert result["abnormality_score"] < 30, "정상 이미지를 비정상으로 잘못 감지했습니다"

@req_id("REQ-007", "REQ-008")
def test_model_metadata_compliance(metadata_url):
    """
    REQ-007: 모델 메타데이터가 규제 요구사항을 준수해야 한다
    REQ-008: 버전 정보가 시맨틱 버전 형식을 따라야 한다
    """
    import re
    
    response = requests.get(metadata_url)
    assert response.status_code == 200
    
    metadata = response.json()
    
    # 필수 필드 확인
    required_fields = ["version", "regulatory_status", "intended_use", 
                       "sensitivity", "specificity", "last_updated", "model_id"]
    
    for field in required_fields:
        assert field in metadata, f"모델 메타데이터에 필수 필드 {field}가 없습니다"
    
    # 버전 형식 확인 (시맨틱 버전)
    version_pattern = r"^\d+\.\d+\.\d+$"  # 예: 1.0.0
    assert re.match(version_pattern, metadata["version"]), \
        f"버전 정보({metadata['version']})가 시맨틱 버전 형식이 아닙니다"

@req_id("REQ-012")
def test_invalid_file_error_handling(api_url, invalid_file):
    """
    REQ-012: 유효하지 않은 이미지 파일 업로드 시 적절한 오류 메시지를 표시해야 한다
    """
    with open(invalid_file, "rb") as f:
        response = requests.post(api_url, files={"file": f})
    
    assert response.status_code == 400
    error_response = response.json()
    
    assert error_response["status"] == "error"
    assert "message" in error_response, "오류 메시지가 제공되지 않았습니다"

@req_id("REQ-014")
def test_large_image_processing(api_url):
    """
    REQ-014: 대용량 이미지(5MB 이상)도 처리할 수 있어야 한다
    """
    import pytest
    from pathlib import Path
    
    # 테스트 데이터 디렉토리에서 large_image.jpg 찾기
    test_data_dir = Path(os.path.dirname(__file__)) / "test_data"
    large_image_path = test_data_dir / "large_image.jpg"
    
    if not large_image_path.exists():
        pytest.skip("대용량 이미지 테스트 파일이 없습니다")
    
    # 이미지 파일 크기 확인
    file_size_mb = large_image_path.stat().st_size / (1024 * 1024)
    assert file_size_mb >= 5, f"테스트 이미지 크기가 5MB 미만입니다: {file_size_mb:.2f}MB"

    with open(large_image_path, "rb") as img:
        response = requests.post(api_url, files={"file": img})
    
    assert response.status_code == 200
    result = response.json()
    
    assert "result" in result, "대용량 이미지 처리 결과가 제공되지 않았습니다" 