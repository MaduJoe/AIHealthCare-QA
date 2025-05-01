import { test, expect } from '@playwright/test';
import { InsightViewerPage } from '../pages/InsightViewerPage';

test('초기 페이지 로드 시 주요 UI 요소가 표시된다', async ({ page }) => {
  const viewer = new InsightViewerPage(page);
  await viewer.goto();

  // Check for the main title/header
  await expect(page.locator('h1').first()).toBeVisible();

  // Check for the file uploader
  // Streamlit's file uploader might not have a specific stable selector easily available
  // Let's check for the button text commonly used in streamlit file_uploader
  await expect(page.getByText('Browse files')).toBeVisible(); // Or the specific text your app uses

  // Check if the analysis button is initially present (it might be disabled until upload)
  await expect(page.getByText('이미지 업로드')).toBeVisible();

  // Check if the download button is initially hidden or disabled (usually appears after analysis)
  // await expect(page.getByText('1234MB', { exact: true })).toBeHidden();
  // await expect(page.getByText('200MB', { exact: true })).toBeVisible();

  // 파일 업로더 컴포넌트 확인
  const dropzone = page.getByTestId('stFileUploaderDropzone');
  await expect(dropzone).toBeVisible();

  // 내부 지시사항 컨테이너
  const instructions = page.getByTestId('stFileUploaderDropzoneInstructions');
  await expect(instructions).toBeVisible();

  // 지시사항 내 텍스트 확인 (작은 글씨)
  const smallText = instructions.locator('small');
  await expect(smallText).toContainText('Limit 200MB per file');
  await expect(smallText).toContainText('JPG, JPEG, PNG');

  // "Browse files" 버튼 확인
  const browseButton = page.getByRole('button', { name: 'Browse files' });
  await expect(browseButton).toBeVisible();
}); 