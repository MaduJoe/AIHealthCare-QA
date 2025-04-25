import { Page } from '@playwright/test';

export class InsightViewerPage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async goto() {
    await this.page.goto('/');
  }

  async uploadImage(imagePath: string) {
    await this.page.getByLabel('이미지 업로드').setInputFiles(imagePath);
  }

  async requestAnalysis() {
    await this.page.getByRole('button', { name: 'AI 판독 요청' }).click();
  }

  async expectResultVisible() {
    await this.page.getByText('AI 결과 요약').isVisible();
  }

  async downloadReport() {
    await this.page.getByRole('button', { name: '리포트 다운로드' }).click();
  }
}
