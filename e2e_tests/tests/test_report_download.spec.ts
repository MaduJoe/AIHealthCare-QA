import { test, expect } from '@playwright/test';
import { InsightViewerPage } from '../pages/InsightViewerPage';

test('AI 결과 보고서를 다운로드할 수 있다', async ({ page }) => {
  const viewer = new InsightViewerPage(page);
  await viewer.goto();
  await viewer.uploadImage('test_data/normal_chest_xray.jpg');
  await viewer.requestAnalysis();
  await viewer.downloadReport();
  // 실제 다운로드 여부는 프로젝트에 따라 다를 수 있음 (추가 구현 필요)
});
