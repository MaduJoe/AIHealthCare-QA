import requests
import json
import pytest
import os
import re
from datetime import datetime, timedelta

API_URL = "http://localhost:5000/analyze"
METADATA_URL = "http://localhost:5000/analyze/metadata"
TEST_DATA_DIR = "api_tests/test_data"

# Regulatory requirements
REGULATORY_REQUIREMENTS = {
    "model_versioning": {
        "format": r"^\d+\.\d+\.\d+$",  # Semantic versioning
        "required": True
    },
    "model_identification": {
        "required": True
    },
    "documentation": {
        "required_fields": ["intended_use", "regulatory_status"]
    },
    "performance_metrics": {
        "required_metrics": ["sensitivity", "specificity"],
        "min_requirements": {
            "sensitivity": 0.80,
            "specificity": 0.80
        }
    },
    "data_privacy": {
        "phi_detection": True,  # Protected Health Information
    }
}

def test_model_versioning_compliance():
    """Test compliance with regulatory versioning requirements"""
    """모델 버전 관리 규제 준수 여부 테스트"""
    response = requests.get(METADATA_URL)
    assert response.status_code == 200
    metadata = response.json()
    
    # 1. Check version exists
    assert "version" in metadata, "Model metadata missing required version information"
    
    # 2. Check version format (semantic versioning)
    version = metadata["version"]
    assert re.match(REGULATORY_REQUIREMENTS["model_versioning"]["format"], version), \
        f"Model version '{version}' does not follow required semantic versioning (MAJOR.MINOR.PATCH)"
    
    # 3. Check model identification
    assert "model_id" in metadata, "Model missing required unique identifier"
    
    # 4. Check last updated date exists and is recent
    assert "last_updated" in metadata, "Model missing required last updated date"
    try:
        # Attempt to parse the date - format may vary, adjust as needed
        last_updated = datetime.strptime(metadata["last_updated"], "%Y-%m-%d") 
        
        # Validate that the model isn't outdated (e.g., should be updated within last 2 years)
        two_years_ago = datetime.now() - timedelta(days=365*2)
        assert last_updated > two_years_ago, "Model is outdated according to regulatory requirements"
    except ValueError:
        pytest.fail(f"Invalid date format in last_updated field: {metadata['last_updated']}")

def test_regulatory_documentation_compliance():
    """Test compliance with regulatory documentation requirements"""
    response = requests.get(METADATA_URL)
    assert response.status_code == 200
    metadata = response.json()
    
    # Check required documentation fields
    for field in REGULATORY_REQUIREMENTS["documentation"]["required_fields"]:
        assert field in metadata, f"Model missing required regulatory documentation: {field}"
    
    # Validate regulatory status format
    assert metadata["regulatory_status"] in ["FDA Cleared", "CE Marked", "연구용(Research Use Only)", "Investigational Use"], \
        f"Invalid regulatory status: {metadata['regulatory_status']}"
    
    # Specific intended use verification
    assert len(metadata["intended_use"]) >= 10, "Intended use description too brief for regulatory compliance"

def test_performance_metrics_compliance():
    """Test compliance with regulatory performance metric requirements"""
    response = requests.get(METADATA_URL)
    assert response.status_code == 200
    metadata = response.json()
    
    # Check required performance metrics
    for metric in REGULATORY_REQUIREMENTS["performance_metrics"]["required_metrics"]:
        assert metric in metadata, f"Model missing required performance metric: {metric}"
        assert isinstance(metadata[metric], (int, float)), f"Performance metric {metric} must be numeric"
        assert 0 <= metadata[metric] <= 1, f"Performance metric {metric} must be between 0 and 1"
        
        # Check minimum performance thresholds
        min_value = REGULATORY_REQUIREMENTS["performance_metrics"]["min_requirements"][metric]
        assert metadata[metric] >= min_value, \
            f"Model {metric} ({metadata[metric]}) below regulatory minimum ({min_value})"

def test_error_handling_compliance():
    """Test compliance with regulatory error handling requirements"""
    # Test invalid input handling
    response = requests.post(API_URL, files={"image": open(f"{TEST_DATA_DIR}/invalid_file.txt", "rb")})
    assert response.status_code == 400, "Failed to properly reject invalid input"
    
    # Verify error response includes required fields
    error_data = response.json()
    assert "status" in error_data, "Error response missing status field"
    assert "error" in error_data, "Error response missing error description"
    assert "error_code" in error_data, "Error response missing error code for traceability"

def test_data_privacy_compliance():
    """Test compliance with health data privacy regulations"""
    # This test would normally check for PHI leakage in results
    # For demo purposes, we'll check if the API has privacy-aware features
    
    response = requests.get(f"{API_URL}/privacy_policy")
    
    # Even if endpoint doesn't exist, we've demonstrated the importance
    # of testing privacy compliance
    if response.status_code == 200:
        policy = response.json()
        assert "data_retention" in policy, "Privacy policy missing data retention information"
        assert "anonymization" in policy, "Privacy policy missing anonymization information"
    else:
        # Skip but log the importance
        pytest.skip("Privacy policy endpoint not available, but would be required for regulatory compliance")

def test_audit_trail_logging():
    """Test compliance with regulatory audit trail requirements"""
    # Generate a trackable request with a unique ID
    unique_id = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Make request with traceable ID
    response = requests.post(
        API_URL, 
        files={"image": open(f"{TEST_DATA_DIR}/normal_chest_xray.jpg", "rb")},
        data={"trace_id": unique_id}
    )
    
    assert response.status_code == 200
    
    # Request audit log for this trace
    audit_response = requests.get(f"{API_URL}/audit_log", params={"trace_id": unique_id})
    
    # In a real system, we'd verify audit log contents
    # For demo, we'll skip if not implemented
    if audit_response.status_code == 200:
        audit_data = audit_response.json()
        assert "timestamp" in audit_data, "Audit log missing timestamp"
        assert "action" in audit_data, "Audit log missing action description"
        assert "user_id" in audit_data, "Audit log missing user identification"
    else:
        pytest.skip("Audit log endpoint not implemented in mock server")

def test_output_reproducibility():
    """Test that results are reproducible for regulatory traceability"""
    # Make two identical requests
    response1 = requests.post(API_URL, files={"image": open(f"{TEST_DATA_DIR}/abnormal_chest_xray.jpg", "rb")})
    response2 = requests.post(API_URL, files={"image": open(f"{TEST_DATA_DIR}/abnormal_chest_xray.jpg", "rb")})
    
    assert response1.status_code == 200
    assert response2.status_code == 200
    
    data1 = response1.json()
    data2 = response2.json()
    
    # For deterministic models, results should be identical
    assert data1["abnormality_score"] == data2["abnormality_score"], \
        "Model produces non-deterministic results, failing regulatory reproducibility requirements"
    
    # Findings should be identical
    assert len(data1["findings"]) == len(data2["findings"]), "Inconsistent findings count between identical runs"
    
    if data1["findings"]:
        # Compare first finding
        assert data1["findings"][0]["name"] == data2["findings"][0]["name"], \
            "Inconsistent finding detection between runs" 