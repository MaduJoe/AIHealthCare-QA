# 📚 LunitCare QA Portfolio

## 🏥 프로젝트 개요

본 프로젝트는 **루닛(Lunit)** 이 추구하는 "AI로 암을 정복한다"는 비전에 깊이 공감하여,  
**의료 AI 제품에 특화된 품질 보증(QA) 자동화 전략**을 설계하고 구현한 포트폴리오입니다.

특히 Lunit INSIGHT/SCOPE 제품군과 같이 **환자의 생명과 직결되는** 의료 시스템의 특성을 고려하여,
단순 기능 검증을 넘어 **신뢰성, 예외처리, 성능, 사용자 경험**을 포괄적으로 검증할 수 있는 테스트 체계를 수립했습니다.

---

## 🎯 주요 목표

- 의료 AI 시스템의 **API 응답 정확성 및 신뢰성 확보**
- **E2E 시나리오 자동화**를 통한 사용자 관점 품질 검증
- **에러 및 예외 상황 시나리오 설계**로 실제 임상 환경 대비
- **CI/CD 자동화**를 통한 빠르고 일관된 품질 유지
- 향후 **ISO13485, FDA 인증** 기준 대응을 고려한 설계

---

## 🛠️ 기술 스택 및 도구

| 분야 | 기술 및 도구 |
|------|-------------|
| API 테스트 | Python, pytest, requests, jsonschema |
| E2E 테스트 | Playwright (TypeScript 기반) |
| Mock 서버 | Flask (Python) |
| CI/CD | GitHub Actions |
| 문서화 | Markdown 기반 (`README`, `test_plan`, `scenario_definitions`) |
| 부하 테스트 | Python + Thread 병렬 요청 스크립트 |

---

## 📁 프로젝트 구성
```bash
lunitcare-qa/ 
├── api_tests/ # API 자동화 테스트 
│ ├── test_analysis_api.py 
│ └── schemas/response_schema.json 
├── e2e_tests/ # Playwright 기반 E2E 시나리오 
│ ├── tests/ 
│ ├── pages/ 
│ └── playwright.config.ts 
├── mock_server/ # Flask 기반 Mock API 서버 
│ └── app.py 
├── stress_tests/ # 부하(Stress) 테스트 
│ └── test_stress_api.py 
├── test_data/ # 테스트용 샘플 이미지 및 파일 
│ └── README.md 
├── docs/ # Test Plan, 시나리오 문서 등 
├── .github/workflows/ci.yml # GitHub Actions 설정 
└── README.md
```
---

## 🧪 테스트 주요 내용

| 영역 | 상세 설명 |
|------|-----------|
| API 테스트 | 정상 이미지, 비정상 입력, 서버 에러 상황 모두 검증 |
| E2E 테스트 | 실제 사용자 흐름(이미지 업로드 → 결과 확인 → 리포트 다운로드) 자동화 |
| 에러 핸들링 | 파일 누락, 파일 타입 오류 등 다양한 예외 상황 검증 |
| 성능 테스트 | 50개 병렬 요청을 통한 API 서버 응답 안정성 검증 |
| 스키마 검증 | API 응답 구조가 명세와 일치하는지 jsonschema로 검증 |
| CI/CD 통합 | 모든 테스트 GitHub Actions를 통해 자동 실행 |

---

## 🏆 포트폴리오 차별화 포인트

- **Playwright POM 구조**로 E2E 테스트 유지보수성 강화
- **Mock Server 다변화** (정상 + 에러 응답 모두 지원)
- **API 스키마 관리 분리**로 대규모 QA 확장성 대비
- **test_data/README 정리**로 데이터 관리 투명성 향상
- **부하(Stress) 테스트**를 통한 실사용 환경 대응성 검증

---

## 📌 추가 문서

- [📋 CHANGELOG.md](./CHANGELOG.md) — 개선 내역 요약
- [📚 면접 대비 QA 시나리오 설명](./docs/qa_scenarios.md) — 테스트 설계 이유 및 전략

---

## 🙌 맺음말

본 프로젝트는 단순 테스트 자동화를 넘어, **"의료 AI 품질 향상을 위한 실질적 QA 전략"** 을 고민하고 반영한 결과물입니다.  
루닛의 미션에 걸맞은 **정확성, 안정성, 확장성**을 갖춘 품질보증 체계 구축에 기여하고 싶습니다.

감사합니다.

---

