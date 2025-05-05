import { test, expect } from '@playwright/test';
import { InsightViewerPage } from '../pages/InsightViewerPage';

test('페이지가 로드되고 올바른 타이틀을 가진다', async ({ page }) => {
  const viewer = new InsightViewerPage(page);
  await viewer.goto();

  // Check the page title - Adjust 'Expected Page Title' to the actual title
  await expect(page).toHaveTitle(/LunitCare - AI 의료 영상 분석/i); // Use regex for flexibility

  // Optional: Check for a key element confirming load, like the main header
  await expect(page.locator('h1')).toContainText('LunitCare AI 의료 영상 분석'); // Adjust selector/text if needed
}); 