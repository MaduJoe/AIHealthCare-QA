# E2E 테스트
이 디렉토리는 의료 영상 분석 애플리케이션의 엔드투엔드(E2E) 테스트를 포함하고 있습니다. Playwright 프레임워크를 사용하여 실제 사용자 환경을 시뮬레이션합니다.
## 테스트 파일 구조

```
e2e_tests/
├── fixtures/          # 테스트 픽스처
├── pages/             # 페이지 객체 모델
├── test_data/         # 테스트 이미지 및 데이터
├── tests/             # 테스트 파일
├── playwright-report/ # HTML 테스트 리포트
├── test-results/      # 테스트 결과 및 스크린샷
├── coverage-analysis.js # 테스트 커버리지 분석 스크립트
├── playwright.config.ts # Playwright 설정
├── package.json       # 의존성 정의
└── README.md          # 이 문서
```

## 테스트 실행 방법

1. **모든 테스트 실행**:
   ```bash
   npx playwright test
   ```

2. **특정 테스트 실행**:
   ```bash
   npx playwright test tests/test_image_upload.spec.ts
   ```

3. **UI 모드로 실행**:
   ```bash
   npx playwright test --ui
   ```

4. **요구사항 추적성을 위한 JSON 리포트 생성**:
   ```bash
   npx playwright test --reporter=json --output=../scripts/temp/e2e_results.json
   ```

## 테스트 설명

### 1. 기본 기능 테스트
- `test_image_upload.spec.ts`: 기본적인 이미지 업로드 기능 테스트
- `test_initial_ui_elements.spec.ts`: 초기 UI 요소들의 존재 여부와 상태 확인
- `test_page_load_and_title.spec.ts`: 페이지 로드 및 타이틀 확인

### 2. 이미지 처리 테스트
- `test_abnormal_image_analysis.spec.ts`: 비정상 이미지에 대한 분석 결과 확인
- `test_invalid_image_upload.spec.ts`: 잘못된 형식의 이미지 업로드 처리
- `test_large_image_upload.spec.ts`: 대용량 이미지 업로드 및 처리

### 3. 분석 결과 테스트
- `test_analysis_result_detail.spec.ts`: 분석 결과의 상세 정보 확인
- `test_re_analysis_attempt.spec.ts`: 이미지 재분석 시도 및 결과 확인

### 4. 보고서 및 다운로드 테스트
- `test_report_download.spec.ts`: 분석 보고서 다운로드 기능
- `test_sequential_upload_analyze_download.spec.ts`: 업로드-분석-다운로드 전체 프로세스

### 5. 요구사항 추적성 테스트
- `test_req_traceability.spec.ts`: ISO 13485 요구사항 추적성을 위한 테스트

## 요구사항 추적성

테스트에 요구사항 ID를 연결하려면 `testUtils.ts`의 `withReqIds` 함수를 사용합니다:

```typescript
import { withReqIds } from '../utils/testUtils';

test('이미지 업로드 테스트', async ({ page }) => {
  await withReqIds(['REQ-001'], '이미지 업로드 테스트', async () => {
    // 테스트 코드
  });
});
```

## 주의사항
1. 테스트 실행 전 `mock API` 서버가 실행 중인지 확인
2. 테스트용 이미지 파일이 `e2e_tests/test_data/` 디렉토리에 있는지 확인
3. 요구사항 추적성을 위한 테스트는 반드시 `withReqIds` 함수를 사용하여 요구사항 ID를 연결 
4. 테스트 실패 시 스크린샷은 `test-results` 디렉토리에 저장됩니다.
5. HTML 형식의 테스트 리포트는 `playwright-report` 디렉토리에서 확인할 수 있습니다.