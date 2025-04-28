# 📋 CHANGELOG.md

## [v1.1] - 2025-04-26

### 🚀 전체 개선 요약
- 프로젝트 구조 고도화 및 Playwright POM 패턴 적용
- API Mock 서버에 에러 응답 추가
- GitHub Actions 기반 CI/CD 파이프라인 구축
- API 테스트케이스 정상/비정상 모두 커버
- Playwright 테스트 스크린샷/비디오 기록 활성화
- `test_data/` 폴더별 파일 설명 문서화
- API 응답 JSON 스키마 파일 분리
- 50병렬 부하(Stress) 테스트 스크립트 작성

### 📂 세부 변경 내역
- `e2e_tests/pages/InsightViewerPage.ts` 생성 (POM)
- `mock_server/app.py`에 `/analyze/error` 엔드포인트 추가
- `.github/workflows/ci.yml` 작성 (pytest + Playwright 자동화)
- `api_tests/test_analysis_api.py` 리팩터링 및 오류 케이스 추가
- `test_data/README.md` 작성 (샘플 파일 설명)
- `api_tests/schemas/response_schema.json` 분리
- `stress_tests/test_stress_api.py` 추가 (간단 병렬 부하테스트)

---

## 🚀 Next Steps
- 부하테스트 정식 도구(`Locust`, `k6`)로 확장 검토
- Playwright E2E 시나리오 추가 (ex: 에러 케이스 흐름)
- 실 서비스와 유사한 이미지 파이프라인 연동 테스트
