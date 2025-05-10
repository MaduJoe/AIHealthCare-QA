#!/usr/bin/env python3
"""
LunitCare QA - ISO 13485 요구사항 추적 리포트 생성기 - CI 또는 수동 실행용 리포트 생성 스크립트

이 스크립트는:
1. pytest 및 playwright 테스트 결과에서 요구사항 추적 데이터 수집 (pytest 실행 결과에서 요구사항 ID별 Pass/Fail 정리)
2. markdown 형식의 추적 매트릭스 생성
3. traceability_matrix.md 파일 자동 업데이트

사용법:
$ python scripts/generate_trace_report.py
"""

import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime
import subprocess
import shutil

# 프로젝트 루트 디렉토리 계산
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
DOCS_DIR = PROJECT_ROOT / "docs"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
TEMP_DIR = SCRIPTS_DIR / "temp"

# 요구사항 정의 파일
REQUIREMENTS_FILE = DOCS_DIR / "requirements.md"
# 추적 매트릭스 파일
TRACEABILITY_MATRIX_FILE = DOCS_DIR / "traceability_matrix.md"
# 테스트 결과 파일
PYTEST_RESULTS_FILE = TEMP_DIR / "req_test_results.json"
E2E_RESULTS_FILE = TEMP_DIR / "e2e_results.json"

# 결과 이모지
PASS_EMOJI = "✅ Pass"
FAIL_EMOJI = "❌ Fail"
SKIP_EMOJI = "⚠️ 미테스트"
PARTIAL_EMOJI = "⚠️ 부분통과"

def parse_requirements():
    """
    요구사항 정의 파일에서 요구사항 목록 파싱
    
    Returns:
        dict: 요구사항 정보 딕셔너리
    """
    requirements = {}
    
    if not REQUIREMENTS_FILE.exists():
        print(f"오류: 요구사항 파일이 없습니다: {REQUIREMENTS_FILE}")
        sys.exit(1)
    
    with open(REQUIREMENTS_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 테이블 정규식 패턴
    table_pattern = r"\|\s*ID\s*\|\s*유형\s*\|\s*설명\s*\|.*?\|\s*버전\s*\|\s*상태\s*\|(.*?)(?:\n\n|\n#|\Z)"
    row_pattern = r"\|\s*(REQ-\d+)\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|"
    
    # 테이블 찾기
    table_match = re.search(table_pattern, content, re.DOTALL)
    if not table_match:
        print("오류: 요구사항 파일에서 테이블을 찾을 수 없습니다.")
        sys.exit(1)
    
    table_content = table_match.group(1)
    
    # 각 행 파싱
    for match in re.finditer(row_pattern, table_content):
        req_id = match.group(1).strip()
        req_type = match.group(2).strip()
        description = match.group(3).strip()
        priority = match.group(4).strip()
        version = match.group(5).strip()
        status = match.group(6).strip()
        
        requirements[req_id] = {
            "id": req_id,
            "type": req_type,
            "description": description,
            "priority": priority,
            "version": version,
            "status": status,
            "tests": [],
            "test_results": []
        }
    
    return requirements

def parse_pytest_results():
    """
    pytest 결과 파일에서 요구사항 ID와 테스트 결과 파싱
    
    Returns:
        dict: 요구사항 ID별 테스트 결과
    """
    if not PYTEST_RESULTS_FILE.exists():
        print(f"경고: pytest 결과 파일이 없습니다: {PYTEST_RESULTS_FILE}")
        return {}
    
    with open(PYTEST_RESULTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def parse_e2e_results():
    """
    Playwright E2E 테스트 결과에서 요구사항 ID 추출
    (테스트 제목 형식: [REQ-001,REQ-002] 테스트 제목)
    
    Returns:
        dict: 요구사항 ID별 테스트 결과
    """
    if not E2E_RESULTS_FILE.exists():
        print(f"경고: E2E 테스트 결과 파일이 없습니다: {E2E_RESULTS_FILE}")
        return {}
    
    with open(E2E_RESULTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    e2e_results = {}
    pattern = r"\[(REQ-\d+(?:,REQ-\d+)*)\]"
    
    for test in data.get("tests", []):
        title = test.get("title", "")
        status = test.get("status", "")
        
        # 요구사항 ID 추출
        match = re.search(pattern, title)
        if match:
            req_ids = match.group(1).split(",")
            test_name = title.replace(match.group(0), "").strip()
            
            for req_id in req_ids:
                if req_id not in e2e_results:
                    e2e_results[req_id] = {"tests": [], "status": "NotRun"}
                
                e2e_results[req_id]["tests"].append(test_name)
                
                # 상태 업데이트
                if status == "passed":
                    if e2e_results[req_id]["status"] != "failed":
                        e2e_results[req_id]["status"] = "passed"
                elif status == "failed":
                    e2e_results[req_id]["status"] = "failed"
    
    return e2e_results

def merge_test_results(requirements, pytest_results, e2e_results):
    """
    pytest 및 E2E 테스트 결과를 요구사항 데이터와 병합
    
    Args:
        requirements (dict): 요구사항 정보
        pytest_results (dict): pytest 테스트 결과
        e2e_results (dict): E2E 테스트 결과
        
    Returns:
        dict: 병합된 요구사항 및 테스트 결과
    """
    # pytest 결과 병합
    for req_id, result in pytest_results.items():
        if req_id in requirements:
            requirements[req_id]["tests"].extend(result.get("tests", []))
            
            if result.get("status") == "Passed":
                requirements[req_id]["test_results"].append(PASS_EMOJI)
            elif result.get("status") == "Failed":
                requirements[req_id]["test_results"].append(FAIL_EMOJI)
            else:
                requirements[req_id]["test_results"].append(SKIP_EMOJI)
    
    # E2E 테스트 결과 병합
    for req_id, result in e2e_results.items():
        if req_id in requirements:
            requirements[req_id]["tests"].extend(result.get("tests", []))
            
            if result.get("status") == "passed":
                requirements[req_id]["test_results"].append(PASS_EMOJI)
            elif result.get("status") == "failed":
                requirements[req_id]["test_results"].append(FAIL_EMOJI)
            else:
                requirements[req_id]["test_results"].append(SKIP_EMOJI)
    
    # 테스트가 없는 요구사항에 미테스트 표시
    for req_id, req in requirements.items():
        if not req["tests"]:
            req["test_results"] = [SKIP_EMOJI]
        
        # 결과가 혼합된 경우 (Pass 및 Fail) 부분통과로 표시
        if PASS_EMOJI in req["test_results"] and FAIL_EMOJI in req["test_results"]:
            req["test_results"] = [PARTIAL_EMOJI]
    
    return requirements

def generate_traceability_matrix(requirements):
    """
    요구사항 및 테스트 결과를 기반으로 추적 매트릭스 생성
    
    Args:
        requirements (dict): 병합된 요구사항 및 테스트 결과
        
    Returns:
        str: 마크다운 형식의 추적 매트릭스
    """
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 매트릭스 헤더
    matrix = [
        "# LunitCare QA 요구사항 추적 매트릭스",
        "",
        "본 문서는 요구사항과 테스트 케이스 간의 추적성을 보여주는 매트릭스입니다.",
        "(이 파일은 `generate_trace_report.py` 스크립트에 의해 자동으로 갱신됩니다)",
        "",
        f"*마지막 업데이트: {today}*",
        "",
        "## 추적 매트릭스",
        "",
        "| 요구사항 ID | 설명 | 테스트 케이스 | 결과 | 비고 |",
        "|-------------|------|--------------|------|------|"
    ]
    
    # 요구사항 목록
    for req_id, req in sorted(requirements.items()):
        # 테스트 케이스 목록
        tests = "<br>".join(req["tests"]) if req["tests"] else "없음"
        
        # 테스트 결과
        results = "<br>".join(req["test_results"])
        
        # 비고
        notes = ""
        if FAIL_EMOJI in req["test_results"]:
            notes = "개선 필요"
        elif PARTIAL_EMOJI in req["test_results"]:
            notes = "일부 테스트 실패"
        elif SKIP_EMOJI in req["test_results"]:
            notes = "테스트 구현 필요"
        
        # 행 추가
        matrix.append(f"| {req_id} | {req['description']} | {tests} | {results} | {notes} |")
    
    # 통계 정보 추가
    total_reqs = len(requirements)
    tested_reqs = sum(1 for req in requirements.values() if req["tests"])
    passed_reqs = sum(1 for req in requirements.values() if PASS_EMOJI in req["test_results"] and FAIL_EMOJI not in req["test_results"])
    failed_reqs = sum(1 for req in requirements.values() if FAIL_EMOJI in req["test_results"])
    partial_reqs = sum(1 for req in requirements.values() if PARTIAL_EMOJI in req["test_results"])
    untested_reqs = sum(1 for req in requirements.values() if not req["tests"])
    
    matrix.extend([
        "",
        "## 테스트 커버리지 요약",
        "",
        f"- **총 요구사항 수**: {total_reqs}",
        f"- **테스트 케이스로 커버된 요구사항**: {tested_reqs} ({tested_reqs/total_reqs:.1%})",
        f"- **테스트 통과 요구사항**: {passed_reqs} ({passed_reqs/total_reqs:.1%})",
        f"- **테스트 실패 요구사항**: {failed_reqs} ({failed_reqs/total_reqs:.1%})",
        f"- **부분 통과 요구사항**: {partial_reqs} ({partial_reqs/total_reqs:.1%})",
        f"- **미테스트 요구사항**: {untested_reqs} ({untested_reqs/total_reqs:.1%})",
        "",
        "## 개선 필요 항목",
        ""
    ])
    
    # 개선 필요 항목 목록
    improvement_needed = []
    
    for req_id, req in sorted(requirements.items()):
        if FAIL_EMOJI in req["test_results"]:
            improvement_needed.append(f"1. **{req_id}** ({req['description']}) - 테스트 실패")
        elif PARTIAL_EMOJI in req["test_results"]:
            improvement_needed.append(f"1. **{req_id}** ({req['description']}) - 일부 테스트 실패")
        elif SKIP_EMOJI in req["test_results"] and not req["tests"]:
            improvement_needed.append(f"1. **{req_id}** ({req['description']}) - 테스트 구현 필요")
    
    if improvement_needed:
        matrix.extend(improvement_needed)
    else:
        matrix.append("모든 요구사항이 테스트를 통과했습니다.")
    
    return "\n".join(matrix)

def run_e2e_tests():
    """
    E2E 테스트 실행 및 결과 저장
    """
    print("E2E 테스트 실행 중...")
    
    # 결과 디렉토리 생성
    TEMP_DIR.mkdir(exist_ok=True, parents=True)
    
    # E2E 테스트 실행 (결과를 JSON으로 저장)
    try:
        e2e_cmd = ["npx", "playwright", "test", "--reporter=json", f"--output={E2E_RESULTS_FILE}"]
        subprocess.run(e2e_cmd, cwd=PROJECT_ROOT / "e2e_tests", check=False)
        print(f"E2E 테스트 결과 저장됨: {E2E_RESULTS_FILE}")
    except Exception as e:
        print(f"E2E 테스트 실행 중 오류 발생: {e}")

def run_pytest_tests():
    """
    pytest 테스트 실행
    """
    print("pytest 테스트 실행 중...")
    
    # 결과 디렉토리 생성
    TEMP_DIR.mkdir(exist_ok=True, parents=True)
    
    # pytest 실행 (conftest.py의 플러그인이 결과를 자동으로 저장)
    try:
        pytest_cmd = ["pytest", "api_tests"]
        subprocess.run(pytest_cmd, cwd=PROJECT_ROOT, check=False)
        print("pytest 테스트 실행 완료")
    except Exception as e:
        print(f"pytest 테스트 실행 중 오류 발생: {e}")

def main():
    """
    메인 함수 - 테스트 실행 및 추적 매트릭스 생성
    """
    # 디렉토리 생성
    TEMP_DIR.mkdir(exist_ok=True, parents=True)
    
    # 명령줄 인수 처리
    run_tests = "--run-tests" in sys.argv
    
    if run_tests:
        # 테스트 실행
        run_pytest_tests()
        run_e2e_tests()
    
    # 요구사항 파싱
    requirements = parse_requirements()
    
    # 테스트 결과 파싱
    pytest_results = parse_pytest_results()
    e2e_results = parse_e2e_results()
    
    # 결과 병합
    merged_requirements = merge_test_results(requirements, pytest_results, e2e_results)
    
    # 추적 매트릭스 생성
    matrix = generate_traceability_matrix(merged_requirements)
    
    # 파일 백업
    if TRACEABILITY_MATRIX_FILE.exists():
        backup_file = TRACEABILITY_MATRIX_FILE.with_suffix(".md.bak")
        shutil.copy2(TRACEABILITY_MATRIX_FILE, backup_file)
        print(f"기존 파일 백업: {backup_file}")
    
    # 결과 저장
    with open(TRACEABILITY_MATRIX_FILE, "w", encoding="utf-8") as f:
        f.write(matrix)
    
    print(f"추적 매트릭스 생성 완료: {TRACEABILITY_MATRIX_FILE}")

if __name__ == "__main__":
    main() 