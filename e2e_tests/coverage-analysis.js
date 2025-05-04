/**
 * E2E 테스트 커버리지 분석 도구
 * 
 * Playwright 테스트의 커버리지를 분석하고 보고서를 생성합니다.
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');

// 테스트 결과 디렉토리
const RESULTS_DIR = path.join(__dirname, 'test-results');
// 보고서 디렉토리
const REPORT_DIR = path.join(__dirname, 'coverage-report');

// 보고서 디렉토리가 없으면 생성
if (!fs.existsSync(REPORT_DIR)) {
  fs.mkdirSync(REPORT_DIR, { recursive: true });
}

/**
 * 테스트 파일 구조 분석
 * 테스트 파일에서 기능별 테스트 케이스를 추출합니다.
 */
function analyzeTestFiles() {
  const testFiles = glob.sync('tests/**/*.spec.{ts,js}', { cwd: __dirname });
  
  const testCases = [];
  const features = new Set();
  
  testFiles.forEach(file => {
    const content = fs.readFileSync(path.join(__dirname, file), 'utf-8');
    const testMatches = content.match(/test\(['"](.+?)['"]/g) || [];
    
    // 테스트 케이스 추출
    const fileCases = testMatches.map(match => {
      const testName = match.match(/test\(['"](.+?)['"]/)[1];
      // 기능 분류 추출 (테스트 이름의 첫 단어를 기준으로)
      const feature = testName.split(' ')[0].replace(/[^가-힣a-zA-Z0-9]/g, '');
      
      features.add(feature);
      
      return {
        file,
        testName,
        feature
      };
    });
    
    testCases.push(...fileCases);
  });
  
  return { testCases, features: Array.from(features) };
}

/**
 * 테스트 결과 분석
 * Playwright 테스트 결과 폴더에서 실행 결과를 분석합니다.
 */
function analyzeTestResults() {
  const resultFiles = glob.sync('**/*-results.json', { cwd: RESULTS_DIR });
  
  const results = [];
  
  resultFiles.forEach(file => {
    try {
      const resultData = JSON.parse(fs.readFileSync(path.join(RESULTS_DIR, file), 'utf-8'));
      
      if (resultData.suites && resultData.suites.length) {
        const suite = resultData.suites[0];
        if (suite.specs && suite.specs.length) {
          suite.specs.forEach(spec => {
            results.push({
              testFile: resultData.config.projects[0].testDir,
              testName: spec.title,
              status: spec.tests[0]?.status || 'unknown',
              duration: spec.tests[0]?.duration || 0
            });
          });
        }
      }
    } catch (error) {
      console.error(`결과 파일 분석 오류 (${file}):`, error.message);
    }
  });
  
  return results;
}

/**
 * 테스트 커버리지 생성
 * 테스트 파일과 결과를 분석하여 커버리지 보고서를 생성합니다.
 */
function generateCoverageReport() {
  const { testCases, features } = analyzeTestFiles();
  const testResults = analyzeTestResults();
  
  // 테스트 케이스별 결과 매핑
  const mappedResults = testCases.map(testCase => {
    const result = testResults.find(r => 
      r.testName === testCase.testName
    );
    
    return {
      ...testCase,
      status: result ? result.status : 'not_run',
      duration: result ? result.duration : 0
    };
  });
  
  // 기능별 통계
  const featureStats = {};
  features.forEach(feature => {
    const featureTests = mappedResults.filter(r => r.feature === feature);
    const passed = featureTests.filter(t => t.status === 'passed').length;
    
    featureStats[feature] = {
      total: featureTests.length,
      passed,
      failed: featureTests.filter(t => t.status === 'failed').length,
      skipped: featureTests.filter(t => t.status === 'skipped').length,
      notRun: featureTests.filter(t => t.status === 'not_run').length,
      coverage: featureTests.length ? (passed / featureTests.length * 100).toFixed(2) : 0
    };
  });
  
  // 전체 통계
  const totalTests = mappedResults.length;
  const totalPassed = mappedResults.filter(r => r.status === 'passed').length;
  const totalCoverage = totalTests ? (totalPassed / totalTests * 100).toFixed(2) : 0;
  
  // HTML 보고서 생성
  const reportData = {
    date: new Date().toLocaleString(),
    totalTests,
    totalPassed,
    totalFailed: mappedResults.filter(r => r.status === 'failed').length,
    totalSkipped: mappedResults.filter(r => r.status === 'skipped').length,
    totalNotRun: mappedResults.filter(r => r.status === 'not_run').length,
    totalCoverage,
    featureStats,
    testResults: mappedResults
  };
  
  generateHtmlReport(reportData);
  
  console.log('테스트 커버리지 분석 완료:');
  console.log(`총 테스트: ${totalTests}, 통과: ${totalPassed}, 실패: ${reportData.totalFailed}`);
  console.log(`전체 커버리지: ${totalCoverage}%`);
  
  return reportData;
}

/**
 * HTML 보고서 생성
 */
function generateHtmlReport(data) {
  // 기능별 통계 테이블 생성
  let featureRows = '';
  Object.entries(data.featureStats).forEach(([feature, stats]) => {
    // 커버리지에 따라 색상 클래스 결정
    const coverageClass = 
      stats.coverage >= 80 ? 'coverage-high' : 
      stats.coverage >= 50 ? 'coverage-medium' : 
      'coverage-low';
    
    featureRows += `
      <tr>
        <td>${feature}</td>
        <td>${stats.total}</td>
        <td>${stats.passed}</td>
        <td>${stats.failed}</td>
        <td>${stats.skipped}</td>
        <td>${stats.notRun}</td>
        <td class="${coverageClass}">${stats.coverage}%</td>
      </tr>
    `;
  });
  
  // 테스트 결과 테이블 생성
  let testRows = '';
  data.testResults.forEach(test => {
    const statusClass = 
      test.status === 'passed' ? 'status-passed' : 
      test.status === 'failed' ? 'status-failed' : 
      test.status === 'skipped' ? 'status-skipped' : 
      'status-not-run';
    
    testRows += `
      <tr>
        <td>${test.file}</td>
        <td>${test.testName}</td>
        <td>${test.feature}</td>
        <td class="${statusClass}">${test.status}</td>
        <td>${test.duration ? (test.duration / 1000).toFixed(2) + 's' : '-'}</td>
      </tr>
    `;
  });
  
  // 커버리지 클래스
  const totalCoverageClass = 
    data.totalCoverage >= 80 ? 'coverage-high' : 
    data.totalCoverage >= 50 ? 'coverage-medium' : 
    'coverage-low';
  
  // HTML 보고서 생성
  const html = `
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>LunitCare QA - E2E 테스트 커버리지 보고서</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      margin: 0;
      padding: 20px;
      color: #333;
    }
    .container {
      max-width: 1200px;
      margin: 0 auto;
    }
    h1, h2 {
      color: #2c3e50;
    }
    .summary-box {
      background-color: #f8f9fa;
      border-radius: 5px;
      padding: 15px;
      margin-bottom: 20px;
      display: flex;
      flex-wrap: wrap;
      gap: 15px;
    }
    .metric {
      flex: 1;
      min-width: 120px;
      padding: 10px;
      border-radius: 5px;
      text-align: center;
    }
    .metric h3 {
      margin-top: 0;
      font-size: 14px;
      text-transform: uppercase;
    }
    .metric p {
      font-size: 24px;
      font-weight: bold;
      margin: 0;
    }
    .total-tests { background-color: #e3f2fd; }
    .passed-tests { background-color: #e8f5e9; }
    .failed-tests { background-color: #ffebee; }
    .skipped-tests { background-color: #fff8e1; }
    .coverage { background-color: #e1f5fe; }
    
    table {
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 20px;
    }
    th, td {
      padding: 8px 12px;
      text-align: left;
      border-bottom: 1px solid #ddd;
    }
    th {
      background-color: #f2f2f2;
      font-weight: bold;
    }
    tr:hover {
      background-color: #f5f5f5;
    }
    
    .status-passed { background-color: #c8e6c9; }
    .status-failed { background-color: #ffcdd2; }
    .status-skipped { background-color: #fff9c4; }
    .status-not-run { background-color: #f5f5f5; }
    
    .coverage-high { background-color: #c8e6c9; }
    .coverage-medium { background-color: #fff9c4; }
    .coverage-low { background-color: #ffcdd2; }
    
    .footer {
      margin-top: 30px;
      text-align: center;
      font-size: 12px;
      color: #777;
    }
    
    @media (max-width: 768px) {
      .metric {
        min-width: 100px;
      }
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>LunitCare QA - E2E 테스트 커버리지 보고서</h1>
    <p>생성 일시: ${data.date}</p>
    
    <div class="summary-box">
      <div class="metric total-tests">
        <h3>총 테스트</h3>
        <p>${data.totalTests}</p>
      </div>
      <div class="metric passed-tests">
        <h3>통과</h3>
        <p>${data.totalPassed}</p>
      </div>
      <div class="metric failed-tests">
        <h3>실패</h3>
        <p>${data.totalFailed}</p>
      </div>
      <div class="metric skipped-tests">
        <h3>스킵</h3>
        <p>${data.totalSkipped + data.totalNotRun}</p>
      </div>
      <div class="metric coverage ${totalCoverageClass}">
        <h3>커버리지</h3>
        <p>${data.totalCoverage}%</p>
      </div>
    </div>
    
    <h2>기능별 커버리지</h2>
    <table>
      <thead>
        <tr>
          <th>기능</th>
          <th>총 테스트</th>
          <th>통과</th>
          <th>실패</th>
          <th>스킵</th>
          <th>미실행</th>
          <th>커버리지</th>
        </tr>
      </thead>
      <tbody>
        ${featureRows}
      </tbody>
    </table>
    
    <h2>테스트 상세 결과</h2>
    <table>
      <thead>
        <tr>
          <th>파일</th>
          <th>테스트 이름</th>
          <th>기능</th>
          <th>상태</th>
          <th>실행 시간</th>
        </tr>
      </thead>
      <tbody>
        ${testRows}
      </tbody>
    </table>
    
    <div class="footer">
      <p>LunitCare QA - 테스트 커버리지 분석 도구</p>
    </div>
  </div>
</body>
</html>
  `;
  
  fs.writeFileSync(path.join(REPORT_DIR, 'coverage-report.html'), html);
  console.log(`HTML 보고서가 생성되었습니다: ${path.join(REPORT_DIR, 'coverage-report.html')}`);
}

// 메인 함수 실행
if (require.main === module) {
  generateCoverageReport();
}

module.exports = {
  analyzeTestFiles,
  analyzeTestResults,
  generateCoverageReport
}; 