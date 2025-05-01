import { test, expect } from '@playwright/test';
import { InsightViewerPage } from '../pages/InsightViewerPage.js';
import { setupTestImages } from '../fixtures/randomImage.js';

test('비정상 소견 이미지를 업로드하고 AI 결과를 확인한다', async ({ page }) => {
  const viewer = new InsightViewerPage(page);
  // TUM 카테고리의 이미지 사용 (종양 이미지)
  const testImages = setupTestImages(1, 'TUM');
  
  await viewer.goto();
  await viewer.uploadImage(testImages[0]);
  await viewer.requestAnalysis();

  // Basic check for analysis completion
  await expect(page.getByText('AI 분석 완료!')).toBeVisible();

  // Future enhancement: Add specific checks for abnormal results if UI provides distinct indicators
  // e.g., await expect(page.locator('[data-testid="abnormality-indicator"]')).toBeVisible();
}); 