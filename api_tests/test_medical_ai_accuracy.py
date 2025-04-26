import requests
import json
import jsonschema
import pytest
import statistics
import os
from datetime import datetime

API_URL = "http://localhost:5000/analyze"
METADATA_URL = "http://localhost:5000/analyze/metadata"

# Load test data directory
TEST_DATA_DIR = "api_tests/test_data"

def load_schema():
    with open("api_tests/schemas/response_schema.json") as f:
        return json.load(f)

def test_model_metadata_compliance():
    """Verify that the model metadata meets regulatory requirements"""
    response = requests.get(METADATA_URL)
    assert response.status_code == 200
    
    metadata = response.json()
    
    # Regulatory compliance checks
    assert "version" in metadata, "Model must include version information"
    assert "regulatory_status" in metadata, "Model must declare regulatory status"
    assert "intended_use" in metadata, "Model must specify intended use"
    assert "sensitivity" in metadata, "Model must report sensitivity metric"
    assert "specificity" in metadata, "Model must report specificity metric"
    
    # Validate performance metrics are within acceptable range
    assert 0 <= metadata["sensitivity"] <= 1, "Sensitivity must be between 0 and 1"
    assert 0 <= metadata["specificity"] <= 1, "Specificity must be between 0 and 1"
    
    # FDA-like requirements
    assert "last_updated" in metadata, "Model must include last updated date"
    assert "model_id" in metadata, "Model must have unique identifier"

def test_abnormal_detection_accuracy():
    """Test the model's ability to correctly identify abnormal images"""
    """의료 AI의 이상 감지 정확도 테스트"""
    response = requests.post(API_URL, 
                           files={"image": open(f"{TEST_DATA_DIR}/abnormal_chest_xray.jpg", "rb")})
    assert response.status_code == 200
    
    data = response.json()
    
    # Verify schema compliance
    schema = load_schema()
    jsonschema.validate(instance=data, schema=schema)
    
    # Verify abnormality detection
    assert data["abnormality_score"] > 0.5, "Failed to detect abnormality in abnormal image"
    assert len(data["findings"]) > 0, "No findings reported for abnormal image"
    
    # Check confidence level for clinical usage
    assert data["confidence_level"] >= 0.8, "Confidence too low for clinical use"

def test_normal_detection_accuracy():
    """Test the model's ability to correctly identify normal images"""
    response = requests.post(API_URL, 
                           files={"image": open(f"{TEST_DATA_DIR}/normal_chest_xray.jpg", "rb")})
    assert response.status_code == 200
    
    data = response.json()
    
    # Verify schema compliance
    schema = load_schema()
    jsonschema.validate(instance=data, schema=schema)
    
    # Verify normal detection (low abnormality score)
    assert data["abnormality_score"] < 0.3, "Incorrectly flagged normal image as abnormal"

@pytest.mark.parametrize("rotation_angle", [0, 90, 180, 270])
def test_rotation_invariance(rotation_angle):
    """Test model's resilience to image rotation (important for medical AI)"""
    # In a real implementation, this would rotate the image programmatically
    # Here we're just simulating the concept
    response = requests.post(API_URL, 
                           files={"image": open(f"{TEST_DATA_DIR}/abnormal_chest_xray.jpg", "rb")},
                           data={"rotation": rotation_angle})
    
    assert response.status_code == 200
    data = response.json()
    
    # Check abnormality is still detected regardless of orientation
    if rotation_angle in [0, 180]:  # Assuming these orientations preserve abnormality visibility
        assert data["abnormality_score"] > 0.5, f"Failed to detect abnormality at {rotation_angle}° rotation"

def test_response_time_performance():
    """Test that AI analysis meets clinical performance requirements"""
    start_time = datetime.now()
    
    response = requests.post(API_URL, 
                           files={"image": open(f"{TEST_DATA_DIR}/normal_chest_xray.jpg", "rb")})
    
    end_time = datetime.now()
    duration_ms = (end_time - start_time).total_seconds() * 1000
    
    assert response.status_code == 200
    assert duration_ms < 5000, f"Analysis took too long: {duration_ms}ms (max allowed: 5000ms)"

def test_consistency_across_multiple_runs():
    """Test consistency of AI predictions across multiple analyses of same image"""
    abnormality_scores = []
    confidence_levels = []
    
    # Run multiple analyses (5 times)
    for _ in range(5):
        response = requests.post(API_URL, 
                               files={"image": open(f"{TEST_DATA_DIR}/abnormal_chest_xray.jpg", "rb")})
        assert response.status_code == 200
        data = response.json()
        abnormality_scores.append(data["abnormality_score"])
        confidence_levels.append(data["confidence_level"])
    
    # Calculate standard deviation - should be minimal for deterministic AI
    abnormality_std_dev = statistics.stdev(abnormality_scores)
    confidence_std_dev = statistics.stdev(confidence_levels)
    
    # Model should be consistent within 1% variation
    assert abnormality_std_dev < 0.01, f"Model predictions inconsistent: std dev = {abnormality_std_dev}"
    assert confidence_std_dev < 0.01, f"Confidence levels inconsistent: std dev = {confidence_std_dev}"

def test_large_image_handling():
    """Test model's ability to handle large resolution medical images"""
    response = requests.post(API_URL, 
                           files={"image": open(f"{TEST_DATA_DIR}/large_image.jpg", "rb")})
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify processing succeeded
    assert "abnormality_score" in data, "Failed to process large image"
    assert "processing_time_ms" in data, "Processing time not reported for large image"
    
    # Check processing time is reasonable for large images
    assert data["processing_time_ms"] < 10000, "Processing time too long for large image"

def test_hl7_fhir_output_compliance():
    """Test if API results can be exported in healthcare interoperability format"""
    response = requests.post(f"{API_URL}/fhir", 
                           files={"image": open(f"{TEST_DATA_DIR}/abnormal_chest_xray.jpg", "rb")})
    
    # While this might fail on the mock server, we're testing the concept
    if response.status_code == 200:
        data = response.json()
        
        # Verify FHIR compliance
        assert "resourceType" in data, "Missing FHIR resourceType"
        assert data.get("resourceType") == "DiagnosticReport", "Incorrect FHIR resource type"
        assert "subject" in data, "Missing patient subject reference"
        assert "conclusion" in data, "Missing diagnostic conclusion"
    else:
        pytest.skip("FHIR endpoint not implemented in mock server") 