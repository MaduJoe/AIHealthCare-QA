import { test, expect } from '@playwright/test';
import { InsightViewerPage } from '../pages/InsightViewerPage.js';
import { setupTestImages } from '../fixtures/randomImage.js';
import * as fs from 'fs';
import * as path from 'path';

test('이미지 파일 크기 제한 확인 (100KB 이하만 허용)', async ({ page }) => {
  const viewer = new InsightViewerPage(page);
  await viewer.goto();

  // 랜덤 이미지 가져오기
  const testImages = setupTestImages(1);
  const imagePath = testImages[0];
  
  // 파일 크기 확인
  const fileSizeInBytes = fs.statSync(imagePath).size;
  const fileSizeInKB = fileSizeInBytes / 1024;
  console.log(`선택된 테스트 이미지 크기: ${fileSizeInKB.toFixed(2)} KB`);
  
  // 이미지 업로드
  await viewer.uploadImage(imagePath);
  
  if (fileSizeInKB <= 100) {
    // 100KB 이하인 경우 - 업로드 성공해야 함
    // 에러 메시지가 없어야 함
    await expect(page.getByText('KB limit', { exact: false })).not.toBeVisible();
    await expect(page.getByText('exceeded', { exact: false })).not.toBeVisible();
    
    // 파일명이 표시되는지 확인
    await expect(page.getByText(path.basename(imagePath))).toBeVisible();
    
    // 분석 버튼이 활성화되어 있어야 함
    const analysisButton = page.getByText('AI 판독 요청');
    await expect(analysisButton).toBeVisible();
    await expect(analysisButton).toBeEnabled();
    
    // 분석 요청 가능해야 함
    await viewer.requestAnalysis();
    await expect(page.getByText('AI 분석 완료!')).toBeVisible({ timeout: 30000 });
  } else {
    // 100KB 초과인 경우 - 업로드 실패해야 함
    // 에러 메시지가 표시되어야 함
    await expect(page.getByText('100', { exact: false })).toBeVisible();
    await expect(page.getByText('KB', { exact: false })).toBeVisible();
    
    // 분석 버튼이 비활성화되거나 보이지 않아야 함
    const analysisButton = page.getByText('AI 판독 요청');
    
    // UI에 따라 다음 중 하나를 사용
    try {
      // 옵션 1: 버튼이 보이지 않음
      await expect(analysisButton).not.toBeVisible();
    } catch (e) {
      // 옵션 2: 버튼이 보이지만 비활성화됨
      await expect(analysisButton).toBeDisabled();
    }
  }
}); 