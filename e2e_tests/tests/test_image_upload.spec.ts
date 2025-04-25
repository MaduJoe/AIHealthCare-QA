import { test, expect } from '@playwright/test';
import { InsightViewerPage } from '../pages/InsightViewerPage';

test('이미지를 업로드하고 AI 결과를 확인한다', async ({ page }) => {
  const viewer = new InsightViewerPage(page);
  await viewer.goto();
  await viewer.uploadImage('test_data/normal_chest_xray.jpg');
  await viewer.requestAnalysis();
  await expect(page.getByText('AI 결과 요약')).toBeVisible();
});
