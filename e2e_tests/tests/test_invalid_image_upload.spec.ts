import { test, expect } from '@playwright/test';
import { InsightViewerPage } from '../pages/InsightViewerPage.js';
import * as path from 'path';
import * as fs from 'fs';

test('유효하지 않은 파일 형식(텍스트)을 업로드하면 오류 메시지가 표시된다', async ({ page }) => {
  const viewer = new InsightViewerPage(page);
  await viewer.goto();
  
  // 테스트용 텍스트 파일 생성 (README.md 같은 허용되지 않는 형식)
  const tempFileName = 'test_invalid_file.txt';
  const tempFilePath = path.join(process.cwd(), tempFileName);
  fs.writeFileSync(tempFilePath, '# This is a markdown file that should be rejected');

  try {
    // 텍스트 파일 업로드
    await viewer.uploadImage(tempFilePath);
    
    // 1. 오류 메시지가 표시되는지 확인
    await expect(page.getByText('files are not allowed')).toBeVisible();
    // 또는 좀 더 구체적으로:
    // await expect(page.getByText('text/markdown files are not allowed')).toBeVisible();
    await expect(page.getByText('are not allowed')).toBeVisible();
    
    // // 2. 오류 아이콘이 표시되는지 확인
    // // Streamlit에서 사용하는 오류 아이콘 요소가 있을 것입니다
    // await expect(page.locator('svg').filter({ hasText: '!' })).toBeVisible();
    
    // 3. 파일 이름이 목록에 표시되는지 확인
    await expect(page.getByText(tempFileName)).toBeVisible();
    
    // // 4. 닫기 버튼(X)이 표시되는지 확인
    // const closeButton = page.locator('button').filter({ hasText: '×' }).first();
    // await expect(closeButton).toBeVisible();
    
    // 5. 분석 버튼이 비활성화되어 있는지 (또는 숨겨져 있는지) 확인
    // (UI에 따라 달라질 수 있음)
    const analysisButton = page.getByText('AI 판독 요청');
    await expect(analysisButton).not.toBeVisible();
    
  } finally {
    // 임시 파일 삭제
    if (fs.existsSync(tempFilePath)) {
      fs.unlinkSync(tempFilePath);
    }
  }
}); 