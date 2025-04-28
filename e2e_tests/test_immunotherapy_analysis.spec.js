const { test, expect } = require('@playwright/test');
const path = require('path');
const fs = require('fs');

// 테스트 설정
const TEST_IMAGE_PATH = path.join(__dirname, 'fixtures', 'test_lung_cancer.jpg');
const BASE_URL = 'http://localhost:8501'; // Streamlit UI 주소

test.describe('면역치료 반응 분석 E2E 시나리오', () => {
  test.beforeEach(async ({ page }) => {
    // 테스트 이미지가 있는지 확인
    test.skip(!fs.existsSync(TEST_IMAGE_PATH), '테스트 이미지가 없습니다.');
    
    // UI 애플리케이션 페이지 로드
    await page.goto(BASE_URL);
    
    // 페이지가 완전히 로드될 때까지 대기
    await page.waitForSelector('h1:has-text("LunitCare AI 의료 영상 분석")');
  });

  test('시나리오 A: 면역치료 반응 분석 전체 흐름', async ({ page }) => {
    // 1단계: 병리 이미지 업로드
    console.log('Step 1: 병리 이미지 업로드 중...');
    
    // 이미지 업로드 버튼 찾기
    const uploadButton = await page.getByRole('button', { name: 'Browse files' });
    expect(uploadButton).toBeTruthy();
    
    // 파일 선택 대화상자 처리
    const fileChooserPromise = page.waitForEvent('filechooser');
    await uploadButton.click();
    const fileChooser = await fileChooserPromise;
    await fileChooser.setFiles(TEST_IMAGE_PATH);
    
    // 업로드 완료를 나타내는 요소 대기
    await page.waitForSelector('text=업로드 완료', { timeout: 10000 });
    console.log('병리 이미지 업로드 완료');
    
    // 2단계: AI 스코어 확인
    console.log('Step 2: AI 스코어 확인 중...');
    
    // 분석 결과가 표시될 때까지 대기
    await page.waitForSelector('text=분석 결과', { timeout: 30000 });
    
    // 비정상 점수(abnormality_score) 요소 확인
    const scoreElement = await page.locator('text=비정상 점수').first();
    await expect(scoreElement).toBeVisible();
    
    // 점수 값 추출
    const scoreText = await page.locator('div.stMarkdown').filter({ hasText: '비정상 점수' }).textContent();
    const scoreValue = parseFloat(scoreText.match(/\d+(\.\d+)?/)[0]);
    console.log(`AI 분석 스코어: ${scoreValue}`);
    
    // 유효한 점수 범위 확인 (0-100)
    expect(scoreValue).toBeGreaterThanOrEqual(0);
    expect(scoreValue).toBeLessThanOrEqual(100);
    
    // 3단계: 치료 적합 판정 표시 확인
    console.log('Step 3: 치료 적합 판정 확인 중...');
    
    // 치료 적합성 섹션 확인
    await page.waitForSelector('text=치료 적합성 평가', { timeout: 5000 });
    
    // 치료 적합성 상태 확인
    const treatmentSuitability = await page.locator('div').filter({ hasText: /적합|부적합/ }).first();
    await expect(treatmentSuitability).toBeVisible();
    
    // 결과에 따라 적합/부적합 로직 확인
    const suitabilityStatus = await treatmentSuitability.textContent();
    console.log(`치료 적합성 판정: ${suitabilityStatus}`);
    
    if (scoreValue > 50) {
      expect(suitabilityStatus).toContain('적합');
    } else {
      expect(suitabilityStatus).toContain('부적합');
    }
    
    // 4단계: 환자 등록 완료
    console.log('Step 4: 환자 등록 진행 중...');
    
    // 환자 등록 버튼 찾기
    const registerButton = await page.getByRole('button', { name: '환자 등록' });
    expect(registerButton).toBeTruthy();
    
    // 환자 정보 입력 폼 열기
    await registerButton.click();
    
    // 환자 정보 입력
    await page.locator('input[placeholder="환자 ID"]').fill('TEST-PT-001');
    await page.locator('input[placeholder="환자 이름"]').fill('테스트환자');
    await page.locator('input[placeholder="생년월일"]').fill('1980-01-01');
    
    // 등록 완료 버튼 클릭
    await page.getByRole('button', { name: '등록 완료' }).click();
    
    // 등록 완료 메시지 확인
    await page.waitForSelector('text=환자 등록이 완료되었습니다', { timeout: 5000 });
    console.log('환자 등록 완료');
    
    // 5단계: 시스템 로그 출력 확인
    console.log('Step 5: 시스템 로그 확인 중...');
    
    // 로그 표시 버튼 찾기
    const logButton = await page.getByRole('button', { name: '시스템 로그 보기' });
    await logButton.click();
    
    // 로그 내용 확인
    await page.waitForSelector('div.log-container', { timeout: 5000 });
    
    // 필요한 로그 메시지 확인
    const logContent = await page.locator('div.log-container').textContent();
    expect(logContent).toContain('분석 완료');
    expect(logContent).toContain('TEST-PT-001'); // 환자 ID가 로그에 있는지 확인
    
    console.log('시스템 로그 확인 완료');
    console.log('테스트 시나리오 완료: 면역치료 반응 분석');
  });
}); 