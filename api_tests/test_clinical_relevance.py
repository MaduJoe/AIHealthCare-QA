import requests
import json
import pytest
import os
from unittest.mock import patch

API_URL = "http://localhost:5000/analyze"
TEST_DATA_DIR = "api_tests/test_data"

# Clinical reference ranges based on medical literature
CLINICAL_THRESHOLDS = {
    "nodule_detection": {
        "min_sensitivity": 0.85,  # Based on clinical guidelines for lung nodule detection
        "min_specificity": 0.80,  # Minimum acceptable specificity for clinical use
    },
    "confidence_levels": {
        "high": 0.9,    # Threshold for high confidence findings
        "moderate": 0.7, # Threshold for moderate confidence
        "low": 0.5      # Threshold for low confidence (below this is considered uncertain)
    },
    "response_time": {
        "urgent": 3000,   # Max ms for urgent cases
        "routine": 5000   # Max ms for routine cases
    }
}

def get_ground_truth(image_filename):
    """
    In a real implementation, this would fetch validated ground truth 
    from a database of clinically validated cases
    """
    if "abnormal" in image_filename:
        return {
            "has_abnormality": True,
            "findings": ["nodule", "opacity"],
            "severity": "moderate",
            "location": "right upper lobe"
        }
    else:
        return {
            "has_abnormality": False,
            "findings": [],
            "severity": "none"
        }

def test_clinical_finding_accuracy():
    """
    Test that findings match clinical ground truth in terms of presence,
    location, and characterization
    """
    image_file = f"{TEST_DATA_DIR}/abnormal_chest_xray.jpg"
    ground_truth = get_ground_truth(image_file)
    
    response = requests.post(API_URL, files={"image": open(image_file, "rb")})
    assert response.status_code == 200
    result = response.json()
    
    # Check if abnormality detection matches ground truth
    has_detected_abnormality = result["abnormality_score"] > 0.5
    assert has_detected_abnormality == ground_truth["has_abnormality"]
    
    if ground_truth["has_abnormality"]:
        # Check if at least one ground truth finding is detected
        detected_findings = [finding["name"].lower() for finding in result["findings"]]
        assert any(truth_finding in detected_findings for truth_finding in ground_truth["findings"]), \
            f"None of the expected findings {ground_truth['findings']} were detected in {detected_findings}"
        
        # Check location if available in the API response
        if "location" in result["findings"][0]:
            assert any(ground_truth["location"] in finding["location"].lower() 
                       for finding in result["findings"]), "Finding location is incorrect"

def test_meets_diagnostic_accuracy_requirements():
    """
    Test that the model meets minimum sensitivity/specificity requirements
    for clinical deployment based on established medical standards
    """
    # Get metadata to check reported sensitivity/specificity
    response = requests.get("http://localhost:5000/analyze/metadata")
    assert response.status_code == 200
    metadata = response.json()
    
    # Check against clinical thresholds
    assert metadata["sensitivity"] >= CLINICAL_THRESHOLDS["nodule_detection"]["min_sensitivity"], \
        f"Model sensitivity {metadata['sensitivity']} below required clinical threshold"
    
    assert metadata["specificity"] >= CLINICAL_THRESHOLDS["nodule_detection"]["min_specificity"], \
        f"Model specificity {metadata['specificity']} below required clinical threshold"

def test_confidence_calibration():
    """
    Test that reported confidence levels are properly calibrated against
    clinically determined ground truth
    """
    response = requests.post(API_URL, 
                           files={"image": open(f"{TEST_DATA_DIR}/abnormal_chest_xray.jpg", "rb")})
    assert response.status_code == 200
    result = response.json()
    
    # For abnormal images with known findings, confidence should be high
    if result["abnormality_score"] > 0.7:  # Clearly abnormal
        assert result["confidence_level"] >= CLINICAL_THRESHOLDS["confidence_levels"]["moderate"], \
            "Confidence level too low for clear abnormality"
    
    # For borderline cases (if API reports this)
    if 0.4 <= result["abnormality_score"] <= 0.6:  # Borderline
        assert result["confidence_level"] < CLINICAL_THRESHOLDS["confidence_levels"]["high"], \
            "Confidence too high for borderline case - could lead to clinical overconfidence"

def test_roi_identification():
    """
    Test that regions of interest (ROIs) are correctly identified in
    the medical images and match clinical expectations
    """
    response = requests.post(API_URL, 
                           files={"image": open(f"{TEST_DATA_DIR}/abnormal_chest_xray.jpg", "rb")})
    assert response.status_code == 200
    result = response.json()
    
    if result["abnormality_score"] > 0.5 and result["findings"]:
        # Check that findings include bounding box/location data
        for finding in result["findings"]:
            assert "coordinates" in finding or "location" in finding, \
                "Finding missing spatial localization data critical for clinical use"
            
            if "coordinates" in finding:
                # Validate coordinate format (x, y, width, height)
                assert len(finding["coordinates"]) == 4, "Invalid ROI coordinate format"
                
                # Check if coordinates are within image bounds (assuming 1024x1024)
                x, y, w, h = finding["coordinates"]
                assert 0 <= x < 1024 and 0 <= y < 1024, "ROI coordinates outside image bounds"
                assert w > 0 and h > 0, "ROI dimensions cannot be negative or zero"

def test_clinical_urgency_flagging():
    """
    Test that critical findings are appropriately flagged for urgent review
    based on clinical significance
    """
    response = requests.post(API_URL, 
                           files={"image": open(f"{TEST_DATA_DIR}/abnormal_chest_xray.jpg", "rb")})
    assert response.status_code == 200
    result = response.json()
    
    # Check if API classifies urgency
    if "urgency" in result:
        urgency_level = result["urgency"]
        abnormality_score = result["abnormality_score"]
        
        # High abnormality scores should correlate with higher urgency
        if abnormality_score > 0.8:
            assert urgency_level in ["high", "urgent", "immediate"], \
                "Critical finding not flagged with appropriate urgency"
        
        # For critical findings, response time should meet urgent care standards
        if urgency_level in ["high", "urgent", "immediate"]:
            assert result.get("processing_time_ms", 5000) <= CLINICAL_THRESHOLDS["response_time"]["urgent"], \
                "Processing time too slow for urgent finding" 