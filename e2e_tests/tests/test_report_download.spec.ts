import { test, expect } from '@playwright/test';
import { InsightViewerPage } from '../pages/InsightViewerPage';
import { setupTestImages } from '../fixtures/randomImage.js';
import * as fs from 'fs';


test('AI 결과 보고서를 다운로드할 수 있다', async ({ page }) => {
  const viewer = new InsightViewerPage(page);
  await viewer.goto();

  // 랜덤 이미지 가져오기
  const testImages = setupTestImages(1);
  const imagePath = testImages[0];
  
  // 이미지 업로드
  await viewer.uploadImage(imagePath);

  await viewer.requestAnalysis();
  await viewer.downloadReport();
  // 실제 다운로드 여부는 프로젝트에 따라 다를 수 있음 (추가 구현 필요)
});
