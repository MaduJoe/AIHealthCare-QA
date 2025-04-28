# 📚 LunitCare QA 프로젝트 통합 문서 - 프로젝트 통합 문서

## 🏥 프로젝트 개요

본 프로젝트는 의료 AI 시스템의 신뢰성과 안전성을 보장하기 위한 종합적인 품질 보증 프레임워크입니다. 실제 AI 모델(google/vit-base-patch16-224)을 활용하여 의료 영상 진단의 정확성, 임상적 유효성, 규제 준수를 체계적으로 검증합니다.

## 🛠️ 기술 스택 및 도구

| 분야 | 기술 및 도구 |
|------|-------------|
| API 테스트 | Python, pytest, requests |
| E2E 테스트 | Playwright (TypeScript 기반) |
| Mock 서버 | Flask, Transformers, PyTorch |
| UI 애플리케이션 | Streamlit |

## 📁 프로젝트 구성
```bash
LunitCare QA 시스템
├── mock_server/         # 의료 영상 분석 API (Flask)
├── api_tests/           # 자동화 테스트 스위트 (pytest)
├── ui_app.py            # 의료진용 대시보드 (Streamlit)
└── e2e_tests/           # 엔드투엔드 테스트 (Playwright)
```

## 🧪 주요 구현 내용

1. **실제 AI 모델 기반 테스트 환경**
   - Vision Transformer 모델을 활용한 이미지 분류
   - 9가지 의료 이미지 클래스 분류 (ADI, BACK, DEB, LYM, MUC, MUS, NORM, STR, TUM)
   - 정확한 API 응답 시뮬레이션

2. **종합적인 QA 전략**
   - REST API 테스트 자동화 (pytest)
   - 웹 UI 테스트 자동화 (Playwright)
   - 성능 및 안정성 검증
   - 의료기기 규제 준수 검증

3. **사용자 중심 검증**
   - 직관적인 의료진용 웹 대시보드
   - 환자 관리 및 결과 리포팅 워크플로우 검증
   - 이미지 업로드부터 분석 결과 확인까지 E2E 테스트

## 📋 변경 이력

### 최신 버전 [v1.1]

- **주요 개선사항**:
  - API Mock 서버에 AI 모델 통합 (google/vit-base-patch16-224)
  - 9개 클래스 의료 이미지 분류 구현
  - 의료진용 웹 대시보드 개선
  - API 테스트케이스 확장

- **세부 변경내역**:
  - `mock_server/app.py`: Transformers 기반 이미지 분류 구현
  - `ui_app.py`: 환자 관리 및 결과 리포팅 기능 강화
  - `api_tests/`: 정상/비정상 응답 검증 테스트 추가
  - `e2e_tests/`: Playwright 기반 사용자 흐름 자동화

## 🔍 QA 핵심 역량

1. **의료 AI 특화 테스트 설계**
   - 의료 이미지 분석의 특성을 고려한 테스트 케이스 구현 (`api_tests/test_medical_ai_accuracy.py`: 9개 클래스별 검증)
   - 9개 클래스 분류 정확도 및 신뢰도 검증 (`mock_server/app.py`: `analyze_image()` 함수의 소프트맥스 확률 계산 및 검증)
   - 경계값 및 예외 케이스 처리 검증 (`ui_app.py`: 오류 처리 로직 내 `add_log()` 함수 활용)

2. **자동화 테스트 프레임워크 구축**
   - API 및 UI 테스트 자동화로 회귀 테스트 효율화 (`e2e_tests/test_image_upload.spec.js`: 이미지 업로드 자동화)
   - 테스트 리포트 자동 생성 및 시각화 (`ui_app.py`: `generate_report_text()` 함수 구현)
   - 지속적 통합/배포(CI/CD) 파이프라인 연계 가능 (`mock_server/app.py`: 상태 코드 기반 에러 처리 표준화)

3. **기술적 문제 해결 능력**
   - 모델-이미지 호환성 이슈 해결 (`mock_server/app.py`: `image.convert("RGB")` 처리)
   - 멀티스레드 환경에서의 안정적 모델 로딩 구현 (`mock_server/app.py`: 모델 객체 초기화 및 장치 할당)
   - Flask와 Streamlit 연동 최적화 (`ui_app.py`: `analyze_image()` 함수 내 API 요청 처리)

4. **의료기기 규제 이해**
   - FDA Software as Medical Device (SaMD) 요구사항 반영 (`ui_app.py`: 위험도 기반 알림 분류)
   - ISO 13485, IEC 62304 등 의료기기 표준 고려 (`ui_app.py`: 분석 결과 추적성 및 로깅 구현)

## 📈 향후 개선 방향

- 부하테스트 확장 (Locust, k6 등 활용)
- 테스트 데이터 관리 시스템 개선
- 설명가능성(Explainability) 검증 추가
- 보안 및 프라이버시 테스트 강화 