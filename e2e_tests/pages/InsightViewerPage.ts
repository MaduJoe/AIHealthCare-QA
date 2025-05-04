// -  Playwright의 POM 패턴을 충실히 따르고 있음.
// - 테스트 로직과 페이지 동작을 명확히 분리하여 재사용성, 유지보수성을 높이기 위함.


import { Page } from '@playwright/test';

export class InsightViewerPage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async goto() {
    await this.page.goto('/');
    // Streamlit app takes a moment to initialize
    await this.page.waitForLoadState('networkidle'); // 웹앱 특성 기반 테스트 튜닝, Streamlit은 React에 비해 느리다.
  }

  async uploadImage(imagePath: string) {
    // Streamlit's file uploader structure
    const fileInput = this.page.locator('input[type="file"]');
    await fileInput.setInputFiles(imagePath);
  }

  async requestAnalysis() {
    // Find the AI 판독 요청 button
    await this.page.getByText('AI 판독 요청').click();

    // // Wait for analysis to complete
    // await this.page.waitForSelector('.stSuccess', { timeout: 10000 }); 

    // ✅ 수정: "AI 분석 완료!" 텍스트를 기다림
    await this.page.getByText('AI 분석 완료!').waitFor({ timeout: 10000 });
  }

  async expectResultVisible() {
    // 백분율(%) 형태로 표시된 점수를 찾음 - 정규식 패턴을 사용하여 백분율을 포함하는 요소를 찾음
    const percentRegex = /\d+(\.\d+)?%/;
    
    // 컨텐츠 로드를 위해 짧게 대기
    await this.page.waitForTimeout(500);
    
    // 엄격 모드 비활성화 + 좀 더 구체적인 셀렉터 사용, 브라우저에서 직접 DOM을 쿼리하는 방식으로 변경
    const scoreLocator = this.page
      .locator('div:not(:has(div))')  // 하위 div가 없는 div만 타겟팅
      .filter({ hasText: percentRegex })
      .first();  // 첫 번째 요소만 선택
    
    await scoreLocator.waitFor({ timeout: 10000 });
    
    // 찾은 점수 출력 (디버깅용)
    const scoreText = await scoreLocator.textContent();
    console.log(`찾은 점수: ${scoreText?.trim()}`); // 찾은 점수를 로그로 출력하여 디버깅 용이
    
    return scoreText;
  }

  // async downloadReport() {
  //   // Find the PDF로 저장 button
  //   await this.page.getByText('결과 저장 (PDF)').click();
  //   // Wait for success message
  //   await this.page.waitForSelector('.stSuccess', { timeout: 5000 });
  // }

  async downloadReport() {
    // 파일 다운로드를 기다리기 시작
    const [ download ] = await Promise.all([
      this.page.waitForEvent('download'),  // 다운로드 이벤트를 기다림 (비동기 흐름 이해도 높음)
      this.page.getByText('결과 저장 (PDF)').click(),  // 버튼 클릭
    ]);
  
    // 다운로드가 실제 발생했는지 체크
    const suggestedFilename = download.suggestedFilename();
    console.log(`다운로드된 파일 이름: ${suggestedFilename}`);
  
    // (선택) 다운로드 파일을 특정 폴더로 저장
    // await download.saveAs('downloads/' + suggestedFilename);
  }
  
}

