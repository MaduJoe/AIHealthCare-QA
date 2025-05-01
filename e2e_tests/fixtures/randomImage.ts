import * as fs from 'fs';
import * as path from 'path';

/**
 * CRC 이미지 중에서 랜덤하게 하나를 선택하는 함수
 * @param count 선택할 이미지 개수 (기본값: 1)
 * @returns 선택된 이미지의 경로 배열
 */
export function selectRandomCRCImages(count: number = 1): string[] {
    const imagesDir = path.join(process.cwd(), 'sampled_crc_images');
    
    // 디렉토리에서 모든 이미지 파일 목록을 가져옴
    const files = fs.readdirSync(imagesDir)
        .filter(file => /\.(jpg|jpeg|png)$/i.test(file));
    
    if (files.length === 0) {
        throw new Error('No CRC images found in the directory');
    }
    
    // 랜덤하게 이미지 선택
    const selectedFiles: string[] = [];
    const availableFiles = [...files];
    
    for (let i = 0; i < Math.min(count, files.length); i++) {
        const randomIndex = Math.floor(Math.random() * availableFiles.length);
        selectedFiles.push(path.join(imagesDir, availableFiles[randomIndex]));
        availableFiles.splice(randomIndex, 1); // 선택된 파일은 제거
    }
    
    return selectedFiles;
}

/**
 * 테스트를 위한 랜덤 CRC 이미지 데이터를 준비하는 setup 함수
 * @param count 필요한 이미지 개수 (기본값: 1)
 * @param category 이미지 카테고리 (ADI, BACK, DEB, LYM, MUC, MUS, NORM, STR, TUM)
 * @returns 테스트에 사용할 이미지 경로 배열
 */
export function setupTestImages(count: number = 1, category?: string): string[] {
    // 프로젝트 루트 디렉토리로 이동
    const projectRoot = path.resolve(__dirname, '..', '..');
    const imagesRootDir = path.join(projectRoot, 'sampled_crc_images');
    
    try {
        let targetDir: string;
        let availableFiles: string[] = [];
        
        // 카테고리가 지정된 경우
        if (category) {
            targetDir = path.join(imagesRootDir, category);
            if (fs.existsSync(targetDir)) {
                // 카테고리 폴더 내의 이미지 파일 가져오기
                availableFiles = fs.readdirSync(targetDir)
                    .filter(file => /\.(jpg|jpeg|png)$/i.test(file))
                    .map(file => path.join(targetDir, file));
            } else {
                throw new Error(`Category directory not found: ${targetDir}`);
            }
        } 
        // 카테고리가 지정되지 않은 경우
        else {
            // 모든 카테고리 폴더 가져오기
            const categories = fs.readdirSync(imagesRootDir)
                .filter(item => {
                    const itemPath = path.join(imagesRootDir, item);
                    return fs.statSync(itemPath).isDirectory();
                });
            
            if (categories.length === 0) {
                throw new Error(`No category directories found in: ${imagesRootDir}`);
            }
            
            // 랜덤하게 카테고리 선택
            const randomCategory = categories[Math.floor(Math.random() * categories.length)];
            targetDir = path.join(imagesRootDir, randomCategory);
            
            // 선택된 카테고리 폴더 내의 이미지 파일 가져오기
            availableFiles = fs.readdirSync(targetDir)
                .filter(file => /\.(jpg|jpeg|png)$/i.test(file))
                .map(file => path.join(targetDir, file));
        }
        
        if (availableFiles.length === 0) {
            throw new Error(`No image files found in directory: ${targetDir}`);
        }
        
        // 랜덤하게 이미지 선택
        const selectedFiles: string[] = [];
        const filesToChooseFrom = [...availableFiles];
        
        for (let i = 0; i < Math.min(count, filesToChooseFrom.length); i++) {
            const randomIndex = Math.floor(Math.random() * filesToChooseFrom.length);
            selectedFiles.push(filesToChooseFrom[randomIndex]);
            filesToChooseFrom.splice(randomIndex, 1);
        }
        
        return selectedFiles;
    } catch (error) {
        console.error('Error in setupTestImages:', error);
        throw error;
    }
}

/**
 * 테스트 후 이미지 관련 리소스를 정리하는 teardown 함수
 * @param imagePaths 테스트에서 사용한 이미지 경로 배열
 */
export function cleanupTestImages(imagePaths: string[]): void {
    // 현재는 특별한 정리 작업이 필요하지 않음
    // 필요시 여기에 캐시 정리, 임시 파일 삭제 등의 로직 추가
    console.log(`Cleanup completed for ${imagePaths.length} test images`);
} 