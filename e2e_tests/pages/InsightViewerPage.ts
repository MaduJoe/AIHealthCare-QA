import { Page } from '@playwright/test';

export class InsightViewerPage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async goto() {
    await this.page.goto('/');
    // Streamlit app takes a moment to initialize
    await this.page.waitForLoadState('networkidle');
  }

  async uploadImage(imagePath: string) {
    // Streamlit's file uploader structure
    const fileInput = this.page.locator('input[type="file"]');
    await fileInput.setInputFiles(imagePath);
  }

  async requestAnalysis() {
    // Find the AI 판독 요청 button
    await this.page.getByText('AI 판독 요청').click();
    // Wait for analysis to complete
    await this.page.waitForSelector('.stSuccess', { timeout: 10000 });
  }

  async expectResultVisible() {
    // Check for the abnormality score section
    await this.page.waitForSelector('[data-testid="ai-score"]', { state: 'attached' });
  }

  async downloadReport() {
    // Find the PDF로 저장 button
    await this.page.getByText('PDF로 저장').click();
    // Wait for success message
    await this.page.waitForSelector('.stSuccess', { timeout: 5000 });
  }
}
