# LunitCare E2E Tests

이 디렉토리는 LunitCare 웹 응용 프로그램에 대한 엔드투엔드 테스트를 포함하고 있습니다.

## 사전 요구 사항

- Node.js 14 이상
- Python 환경에서 Streamlit UI 앱이 실행 중이어야 함
- Mock API 서버가 실행 중이어야 함

## 설치

다음 명령어로 필요한 패키지를 설치합니다:

```bash
npm install
npx playwright install
```

## 테스트 실행

다음 명령어로 테스트를 실행합니다:

```bash
npm test
# 또는
npx playwright test
```

## 테스트 보고서 확인

테스트가 완료되면 HTML 보고서를 확인할 수 있습니다:

```bash
npx playwright show-report
```

## 구조

- `tests/`: 테스트 케이스 파일
- `pages/`: 페이지 객체 모델 파일
- `playwright.config.ts`: Playwright 설정 파일

## 주의 사항

테스트를 실행하기 전에 반드시 다음 서버가 실행 중이어야 합니다:

1. Streamlit UI 앱 (localhost:8501)
2. Mock API 서버 (localhost:5000)

실행 방법:

```bash
# 한 터미널에서 UI 앱 실행
cd <project_root>
streamlit run ui_app.py

# 다른 터미널에서 Mock 서버 실행
cd <project_root>/mock_server
python app.py
``` 