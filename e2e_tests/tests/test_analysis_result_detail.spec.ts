import { test, expect } from '@playwright/test';
import { InsightViewerPage } from '../pages/InsightViewerPage.js';
import { setupTestImages } from '../fixtures/randomImage.js';

test('분석 완료 후 AI 스코어 결과가 표시된다', async ({ page }) => {
  const viewer = new InsightViewerPage(page);
  const testImages = setupTestImages(1);
  
  await viewer.goto();
  await viewer.uploadImage(testImages[0]);
  await viewer.requestAnalysis();

  // 점수 요소가 표시될 때까지 기다리고 점수를 가져옴
  const scoreText = await viewer.expectResultVisible();
  
  // 백분율 형식인지 확인
  expect(scoreText).toMatch(/\d+(\.\d+)?%/);
  
  // 선택적: 점수가 특정 범위 내에 있는지 확인 (예: 0-100%)
  if (scoreText) {
    const numericValue = parseFloat(scoreText.replace('%', ''));
    expect(numericValue).toBeGreaterThanOrEqual(0);
    expect(numericValue).toBeLessThanOrEqual(100);
  }
}); 