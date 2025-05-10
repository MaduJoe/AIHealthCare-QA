# E2E 테스트

## 테스트 파일 구조

```
e2e_tests/
├── tests/
│   ├── test_abnormal_image_analysis.spec.ts    # 비정상 이미지 분석 테스트
│   ├── test_analysis_result_detail.spec.ts     # 분석 결과 상세 정보 테스트
│   ├── test_image_upload.spec.ts               # 기본 이미지 업로드 테스트
│   ├── test_initial_ui_elements.spec.ts        # 초기 UI 요소 테스트
│   ├── test_invalid_image_upload.spec.ts       # 잘못된 이미지 업로드 테스트
│   ├── test_large_image_upload.spec.ts         # 대용량 이미지 업로드 테스트
│   ├── test_page_load_and_title.spec.ts        # 페이지 로드 및 타이틀 테스트
│   ├── test_re_analysis_attempt.spec.ts        # 재분석 시도 테스트
│   ├── test_report_download.spec.ts            # 보고서 다운로드 테스트
│   ├── test_req_traceability.spec.ts           # 요구사항 추적성 테스트
│   └── test_sequential_upload_analyze_download.spec.ts  # 순차적 업로드/분석/다운로드 테스트
├── utils/
│   ├── imageSelector.ts                        # 이미지 선택 유틸리티
│   └── testUtils.ts                           # 테스트 유틸리티
└── playwright.config.ts                        # Playwright 설정 파일
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

1. 테스트 실행 전 mock 서버가 실행 중인지 확인
2. 테스트용 이미지 파일이 `e2e_tests/test-images/` 디렉토리에 있는지 확인
3. 요구사항 추적성을 위한 테스트는 반드시 `withReqIds` 함수를 사용하여 요구사항 ID를 연결 