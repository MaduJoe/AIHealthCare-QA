# Medical AI Quality Assurance Testing Suite

이 디렉토리는 의료 AI 시스템의 품질 보증(QA)을 위한 종합적인 테스트 도구를 포함하고 있습니다. 단순한 기능 검증을 넘어 의료 AI의 정확성과 신뢰성을 검증하기 위한 첨단 테스트 방법론을 구현했습니다.

## 주요 테스트 모듈

### 1. 기본 API 테스트 (`test_analysis_api.py`)
- 기본적인 API 응답 유효성 검증
- 에러 처리 및 예외 상황 테스트

### 2. 의료 AI 정확도 테스트 (`test_medical_ai_accuracy.py`)
- 모델 메타데이터 규제 준수 검증
- 비정상 이미지 감지 정확도 테스트
- 정상 이미지 분류 정확도 테스트
- 이미지 회전 불변성 테스트
- 응답 시간 성능 테스트
- 다중 분석 일관성 테스트
- 대용량 이미지 처리 능력 테스트
- HL7 FHIR 출력 호환성 테스트

### 3. 임상 관련성 테스트 (`test_clinical_relevance.py`)
- 임상 소견 정확도 검증
- 진단 정확도 요구사항 충족 검증
- 신뢰도 보정 테스트
- 관심 영역(ROI) 식별 테스트
- 임상적 긴급성 플래깅 테스트

### 4. 규제 준수 테스트 (`test_regulatory_compliance.py`)
- 모델 버전 관리 준수 테스트
- 규제 문서화 준수 테스트
- 성능 메트릭 준수 테스트
- 오류 처리 준수 테스트
- 데이터 개인정보 보호 준수 테스트
- 감사 추적 로깅 테스트
- 출력 재현성 테스트

## 테스트 데이터

`test_data/` 디렉토리에 다음과 같은 테스트 이미지가 포함되어 있습니다:

| 파일명 | 설명 | 용도 |
|--------|------|------|
| normal_chest_xray.jpg | 정상 흉부 X-ray | 정상 감지 정확도 테스트 |
| abnormal_chest_xray.jpg | 비정상 X-ray (결절 포함) | 비정상 감지 정확도 테스트 |
| invalid_file.txt | 이미지가 아닌 파일 | 오류 처리 테스트 |
| large_image.jpg | 대용량 이미지 | 성능 및 확장성 테스트 |

## 테스트 실행 방법

1. 필수 패키지 설치:
```bash
pip install -r requirements.txt
```

2. 전체 테스트 실행:
```bash
pytest
```

3. 특정 테스트 모듈 실행:
```bash
# 의료 AI 정확도 테스트 실행
cd api_tests
pytest test_medical_ai_accuracy.py -v

# 임상 관련성 테스트 실행
pytest test_clinical_relevance.py -v

# 규제 준수 테스트 실행
pytest test_regulatory_compliance.py -v
```

4. 세부 출력으로 실행:
```bash
pytest -v
```

5. 병렬 테스트 실행 (빠른 실행):
```bash
pytest -xvs -n auto
```

## 보고서 생성

테스트 실행 후 자세한 보고서를 생성하려면:

```bash
pytest --html=report.html
```

## 규제 준수 정보

이 테스트 프레임워크는 다음과 같은 의료기기 소프트웨어 규제 지침을 고려하여 설계되었습니다:

- FDA Software as a Medical Device (SaMD) 지침
- IEC 62304 의료기기 소프트웨어 라이프사이클 프로세스
- ISO 13485 품질 관리 시스템
- ISO 14971 의료기기 위험 관리
- HIPAA 및 GDPR 개인정보 규정

## Runit QA 핵심 원칙

단순한 기능 검증을 넘어선 의학적 AI의 정확성과 신뢰성을 검증하는 QA 전략:

1. **임상적 연관성 검증**: AI 출력이 실제 임상 환경에서 의미 있는지 검증
2. **재현성 및 일관성 보장**: 동일 입력에 대해 일관된 출력 보장
3. **엄격한 성능 평가**: 민감도, 특이도 등 의학적 성능 지표 검증
4. **규제 준수 확인**: 의료기기 규제 요구사항 충족 여부 검증
5. **임상 안전성 중심**: 위양성/위음성 특히 중요 병변 누락 위험 평가 