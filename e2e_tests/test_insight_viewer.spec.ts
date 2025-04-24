import { test, expect, Page } from '@playwright/test'

// 페이지 객체 모델(POM) 사용하여 테스트 코드 구조화
class InsightViewerPage {
  readonly page: Page;
  
  constructor(page: Page) {
    this.page = page;
  }
  
  async goto() {
    await this.page.goto('http://localhost:8501');
  }
  
  async uploadImage(imagePath: string) {
    await this.page.getByLabel('이미지 업로드').setInputFiles(imagePath);
  }
  
  async requestAnalysis() {
    await this.page.getByRole('button', { name: 'AI 판독 요청' }).click();
  }
  
  async waitForResults() {
    // 결과 로딩이 완료될 때까지 대기
    await this.page.getByText('AI 결과 요약').waitFor({ state: 'visible' });
    // 추가 렌더링 시간을 위한 짧은 대기
    await this.page.waitForTimeout(1000);
  }
  
  async getAbnormalityScore() {
    const scoreElement = this.page.getByTestId('ai-score');
    await expect(scoreElement).toBeVisible();
    const scoreText = await scoreElement.textContent() || '';
    return parseFloat(scoreText.replace('%', '').trim());
  }
  
  async getDetectedFlags() {
    const flagElements = await this.page.getByTestId('ai-flag').all();
    const flags: string[] = [];
    
    for (const el of flagElements) {
      const text = await el.textContent();
      if (text) flags.push(text.trim());
    }
    
    return flags;
  }
  
  async toggleAnnotationVisibility() {
    await this.page.getByRole('checkbox', { name: '병변 표시' }).click();
  }
  
  async captureScreenshot(path: string) {
    await this.page.screenshot({ path });
  }
  
  async changeZoomLevel(level: string) {
    await this.page.getByLabel('확대/축소').selectOption(level);
  }
  
  async exportReport() {
    await this.page.getByRole('button', { name: '보고서 다운로드' }).click();
  }
}

// 기본 워크플로우 테스트
test('기본 의료 영상 분석 워크플로우 테스트', async ({ page }) => {
  const insightViewer = new InsightViewerPage(page);
  await insightViewer.goto();
  await insightViewer.uploadImage('samples/abnormal_chest_xray.jpg');
  await insightViewer.requestAnalysis();
  await insightViewer.waitForResults();
  
  // 결과 확인
  await expect(page.getByText('AI 결과 요약')).toBeVisible();
  await expect(page.getByTestId('ai-score')).toContainText('%');
  
  // 스크린샷 캡처 (시각적 확인용)
  await insightViewer.captureScreenshot('test-results/basic-workflow.png');
});

// 정상 vs 비정상 이미지 테스트
test('정상 및 비정상 이미지 결과 차이 확인', async ({ page }) => {
  const insightViewer = new InsightViewerPage(page);
  
  // 정상 이미지 테스트
  await insightViewer.goto();
  await insightViewer.uploadImage('samples/normal_chest_xray.jpg');
  await insightViewer.requestAnalysis();
  await insightViewer.waitForResults();
  
  const normalScore = await insightViewer.getAbnormalityScore();
  const normalFlags = await insightViewer.getDetectedFlags();
  
  // 비정상 이미지 테스트
  await insightViewer.goto();
  await insightViewer.uploadImage('samples/abnormal_chest_xray.jpg');
  await insightViewer.requestAnalysis();
  await insightViewer.waitForResults();
  
  const abnormalScore = await insightViewer.getAbnormalityScore();
  const abnormalFlags = await insightViewer.getDetectedFlags();
  
  // 결과 비교
  expect(abnormalScore).toBeGreaterThan(normalScore);
  expect(abnormalFlags.length).toBeGreaterThan(normalFlags.length);
});

// 영상 조작 기능 테스트
test('의료 영상 조작 기능 테스트', async ({ page }) => {
  const insightViewer = new InsightViewerPage(page);
  await insightViewer.goto();
  await insightViewer.uploadImage('samples/abnormal_chest_xray.jpg');
  await insightViewer.requestAnalysis();
  await insightViewer.waitForResults();
  
  // 주석(병변 표시) 토글 테스트
  await insightViewer.toggleAnnotationVisibility();
  await expect(page.getByTestId('annotation-overlay')).not.toBeVisible();
  await insightViewer.toggleAnnotationVisibility();
  await expect(page.getByTestId('annotation-overlay')).toBeVisible();
  
  // 확대/축소 기능 테스트
  await insightViewer.changeZoomLevel('150%');
  await expect(page.getByTestId('image-viewer')).toHaveAttribute('data-zoom', '150');
  
  // 스크린샷 캡처
  await insightViewer.captureScreenshot('test-results/image-manipulation.png');
});

// 보고서 생성 및 다운로드 테스트
test('분석 보고서 생성 기능 테스트', async ({ page }) => {
  const insightViewer = new InsightViewerPage(page);
  await insightViewer.goto();
  await insightViewer.uploadImage('samples/abnormal_chest_xray.jpg');
  await insightViewer.requestAnalysis();
  await insightViewer.waitForResults();
  
  // 파일 다운로드 다이얼로그 감지를 위한 Promise 생성
  const downloadPromise = page.waitForEvent('download');
  
  // 보고서 다운로드 버튼 클릭
  await insightViewer.exportReport();
  
  // 다운로드 완료 대기
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toContain('.pdf');
});

// 오류 처리 테스트
test('시스템 오류 처리 능력 테스트', async ({ page }) => {
  const insightViewer = new InsightViewerPage(page);
  await insightViewer.goto();
  
  // 잘못된 이미지 형식 업로드 시도
  await insightViewer.uploadImage('samples/invalid_file.txt');
  await insightViewer.requestAnalysis();
  
  // 오류 메시지 확인
  await expect(page.getByText('유효하지 않은 이미지 파일입니다')).toBeVisible();
  
  // 서버 오류 상황 테스트 (서버가 이를 시뮬레이션하도록 설정되어 있어야 함)
  await page.route('**/analyze', route => {
    route.fulfill({
      status: 500,
      contentType: 'application/json',
      body: JSON.stringify({ error: 'Internal server error' })
    });
  });
  
  await insightViewer.uploadImage('samples/normal_chest_xray.jpg');
  await insightViewer.requestAnalysis();
  
  // 오류 처리 UI 확인
  await expect(page.getByText('서버에 문제가 발생했습니다')).toBeVisible();
});
