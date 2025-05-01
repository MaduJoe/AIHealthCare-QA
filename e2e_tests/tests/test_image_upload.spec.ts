import { test, expect } from '@playwright/test';
import { InsightViewerPage } from '../pages/InsightViewerPage.js';
import { setupTestImages } from '../fixtures/randomImage.js';

test('이미지를 업로드하고 AI 결과를 확인한다', async ({ page }) => {
  const viewer = new InsightViewerPage(page);
  const testImages = setupTestImages(1);
  
  await viewer.goto();
  await viewer.uploadImage(testImages[0]);
  await viewer.requestAnalysis();
  await expect(page.getByText('AI 분석 완료!')).toBeVisible();
});