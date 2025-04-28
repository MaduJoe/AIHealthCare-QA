# LunitCare QA E2E 테스트

이 디렉토리는 Playwright를 사용한 LunitCare 의료 영상 분석 애플리케이션의 엔드투엔드(E2E) 테스트를 포함하고 있습니다.

## 설치 및 설정

1. Node.js 설치(14.x 이상)
2. 의존성 설치:
   ```bash
   cd e2e_tests
   npm install
   ```
3. Playwright 브라우저 설치:
   ```bash
   npx playwright install
   ```

## 테스트 실행

### 모든 브라우저에서 테스트 실행
```bash
npm test
```

### 특정 브라우저에서 테스트 실행
```bash
# Chrome에서만 실행
npm run test:chrome

# Firefox에서만 실행
npm run test:firefox

# Safari에서만 실행
npm run test:safari

# 모바일 Chrome에서 실행
npm run test:mobile
```

### 디버그 모드로 테스트 실행
```bash
npm run debug
```

### 테스트 결과 리포트 보기
```bash
npm run report
```

## 테스트 파일 구조

- `fixtures/` - 테스트에 사용되는 이미지 파일 등의 테스트 데이터
- `*.spec.js` - 테스트 시나리오 파일
- `playwright.config.js` - Playwright 설정

## 사용 가능한 테스트 시나리오

### 면역치료 반응 분석 시나리오
`test_immunotherapy_analysis.spec.js` 파일에서 다음 시나리오를 테스트합니다:

1. 병리 이미지 업로드
2. AI 스코어 확인
3. 치료 적합 판정 표시
4. "환자 등록" 완료
5. 시스템 로그 출력 확인

## 테스트 데이터 추가

테스트 이미지를 `fixtures/` 디렉토리에 추가해야 합니다:
- `test_lung_cancer.jpg` - 폐암 테스트 이미지 