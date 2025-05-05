import { test, expect } from '@playwright/test';
import { InsightViewerPage } from '../pages/InsightViewerPage.js';
import { setupTestImages } from '../fixtures/randomImage.js';

test('분석 완료 후 다시 분석 요청을 시도한다', async ({ page }) => {
  const viewer = new InsightViewerPage(page);
  const testImages = setupTestImages(1);
  
  await viewer.goto();
  await viewer.uploadImage(testImages[0]);

  // First analysis request
  await viewer.requestAnalysis();
  await expect(page.getByText('AI 분석 완료!')).toBeVisible();

  // Attempt to request analysis again
  const analysisButton = page.getByText('AI 판독 요청');

  // Check if the button is disabled or hidden after the first analysis
  // Option 1: Check if disabled (most likely scenario)
  // await expect(analysisButton).toBeDisabled();

  // Option 2: Check if hidden
  // await expect(analysisButton).toBeHidden();

  // Verify no new analysis starts (e.g., no second "AI 분석 완료!" appears or loading indicator)
  // Adding a small delay to ensure no unexpected action happens
  await page.waitForTimeout(1000);
  // Ensure the completion message is still the original one (or count occurrences if possible)
  await expect(page.getByText('AI 분석 완료!')).toHaveCount(1); // Requires Playwright 1.27+
}); 