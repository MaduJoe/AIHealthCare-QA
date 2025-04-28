const { defineConfig, devices } = require('@playwright/test');

/**
 * LunitCare QA E2E 테스트 설정
 * @see https://playwright.dev/docs/test-configuration
 */
module.exports = defineConfig({
  testDir: './',
  timeout: 60 * 1000, // 테스트 타임아웃: 60초
  expect: {
    timeout: 10000 // expect의 기본 타임아웃: 10초
  },
  
  // 실패한 테스트에 대한 재시도 횟수
  retries: process.env.CI ? 2 : 1,
  
  // 병렬 테스트 설정
  workers: process.env.CI ? 1 : undefined,
  
  // 테스트 완료 후 리포트
  reporter: [
    ['html', { open: 'never' }], // HTML 리포트 생성
    ['list']                     // 콘솔 출력
  ],
  
  // 테스트 환경 설정
  use: {
    // 브라우저 네비게이션 타임아웃
    navigationTimeout: 30000,
    
    // 스크린샷 캡처 설정
    screenshot: 'only-on-failure',
    
    // 테스트 실행 중 트레이스 수집
    trace: 'retain-on-failure',
    
    // 비디오 녹화 (실패 시에만)
    video: 'on-first-retry'
  },
  
  // 테스트 프로젝트 설정
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
    },
  ],
  
  // 로컬 개발 서버 시작 설정
  webServer: {
    command: 'cd .. && python ui_app.py',
    url: 'http://localhost:8501',
    reuseExistingServer: true,
    timeout: 60000,
  },
}); 