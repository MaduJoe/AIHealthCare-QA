import { test as baseTest, expect } from '@playwright/test';
import { InsightViewerPage } from '../pages/InsightViewerPage';
import { setupTestImages } from '../fixtures/randomImage.js';

/**
 * 요구사항 ID를 테스트 제목에 추가하는 테스트 확장
 */
const test = baseTest.extend({
  // 기본 테스트를 확장하여 요구사항 ID 추적 기능 추가
});

/**
 * 요구사항 ID를 테스트 제목에 포함시키는 유틸리티 함수
 * @param reqIds 요구사항 ID 배열
 * @param title 원래 테스트 제목
 * @returns 요구사항 ID가 포함된 테스트 제목
 */
function withReqIds(reqIds: string[], title: string): string {
  return `[${reqIds.join(',')}] ${title}`;
}

// REQ-001, REQ-010: 이미지 업로드 기능 및 UI 직관성
test(withReqIds(['REQ-001', 'REQ-010'], '이미지 업로드 컴포넌트가 제대로 표시된다'), async ({ page }) => {
  const viewer = new InsightViewerPage(page);
  await viewer.goto();

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

// REQ-011: 페이지 제목이 "LunitCare - AI 의료 영상 분석"를 포함해야 한다
test(withReqIds(['REQ-011'], '페이지가 올바른 제목을 가지고 있다'), async ({ page }) => {
  const viewer = new InsightViewerPage(page);
  await viewer.goto();

  // Streamlit 페이지 제목 확인
  await expect(page).toHaveTitle(/LunitCare - AI 의료 영상 분석/i);
});

// REQ-002: 분석 후 'AI 분석 완료!' 메시지가 표시되어야 한다
test(withReqIds(['REQ-002'], '이미지 분석 후 완료 메시지가 표시된다'), async ({ page }) => {
  const viewer = new InsightViewerPage(page);
  await viewer.goto();


  // 테스트 이미지 경로
  const testImages = setupTestImages(1);

  // 이미지 업로드
  await viewer.uploadImage(testImages[0]);

  // 분석 버튼 클릭
  await page.getByRole('button', { name: 'AI 판독 요청' }).click();

  // 분석 로딩 표시
  await page.getByText('AI가 이미지를 분석 중입니다...').waitFor();

  // 성공 메시지 확인
  await page.getByText('AI 분석 완료!').waitFor({ timeout: 10000 });
  await expect(page.getByText('AI 분석 완료!')).toBeVisible();
});

// REQ-012: 유효하지 않은 이미지 업로드 시 오류 메시지 표시
test(withReqIds(['REQ-012'], '유효하지 않은 파일 업로드 시 오류 메시지가 표시된다'), async ({ page }) => {
  const viewer = new InsightViewerPage(page);
  await viewer.goto();

  // 유효하지 않은 테스트 파일 경로
  const invalidFilePath = 'test_data/invalid_file.txt';

  // 파일 업로드
  await viewer.uploadImage(invalidFilePath);

  // 분석 버튼 클릭
//   await page.getByRole('button', { name: 'AI 판독 요청' }).click();
  const analysisButton = page.getByText('AI 판독 요청');
  await expect(analysisButton).not.toBeVisible();

  // 오류 메시지 확인
//   await page.getByText('분석 실패. 다시 시도해주세요.').waitFor({ timeout: 5000 });
  await expect(page.getByText('not allowed.')).toBeVisible();
}); 