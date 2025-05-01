import { test, expect } from '@playwright/test';
import { InsightViewerPage } from '../pages/InsightViewerPage.js';
import { setupTestImages } from '../fixtures/randomImage.js';
import path from 'path';

test('이미지 업로드, 분석, 보고서 다운로드를 순차적으로 실행한다', async ({ page }) => {
  const viewer = new InsightViewerPage(page);
  const testImages = setupTestImages(1);
  
  // 1. Go to page
  await viewer.goto();

  // 2. Upload image
  await viewer.uploadImage(testImages[0]);
  // Add a small wait or check if upload confirmation is shown if necessary
  await expect(page.getByText(path.basename(testImages[0]))).toBeVisible();

  // 3. Request Analysis
  await viewer.requestAnalysis();
  await expect(page.getByText('AI 분석 완료!')).toBeVisible();

  // 4. Download Report
  await viewer.downloadReport();
  // Check for the success message related to download
  await expect(page.locator('.stSuccess').last()).toContainText('저장 완료'); // Adjust selector/text if needed
}); 