# Test Data for API Testing

This directory contains sample medical images used for testing the API functionality.

## Required Test Images

The following test images should be placed in this directory:

1. `normal_chest_xray.jpg` - A normal chest X-ray image used for basic API testing
2. `abnormal_chest_xray.jpg` - An abnormal chest X-ray with visible nodules
3. `invalid_file.txt` - A non-image text file used to test API error handling

## Image Format Requirements

- All X-ray images should be in JPG or PNG format
- Recommended resolution: 1024x1024 pixels
- Images should be anonymized and contain no patient identifiable information

## Usage

These images are referenced in the following test files:
- `api_tests/test_analysis_api.py`
- `test_stress_api.py`

# 📁 test_data 디렉토리 설명

이 디렉토리는 테스트 자동화 과정에서 사용되는 다양한 입력 데이터를 제공합니다.

| 파일명 | 설명 |
|--------|------|
| normal_chest_xray.jpg | 정상 흉부 X-ray 이미지 (AI 정상 판독 테스트용) |
| abnormal_chest_xray.jpg | 비정상 (병변이 있는) 흉부 X-ray 이미지 (AI 이상 판독 테스트용) |
| invalid_file.txt | 이미지가 아닌 잘못된 파일 (에러 처리 시나리오 테스트용) |
| large_image.jpg | 큰 용량의 이미지 파일 (업로드 성능 및 에러 테스트용) |

---

이 데이터들은 Mock Server (`Flask`) 기반 AI 판독 API 및 Playwright 기반 E2E 시나리오 테스트에 사용됩니다.
