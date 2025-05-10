import pytest
import requests
import subprocess
import time
import os
import logging
from pathlib import Path
import json
from _pytest.config import Config
from _pytest.reports import TestReport

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define test constants
API_BASE_URL = "http://localhost:5000"
# 경로 처리를 위해 Path 객체 사용
TEST_DATA_DIR = Path(os.path.dirname(__file__)) / "test_data"

# 요구사항 추적을 위한 전역 저장소
REQUIREMENT_TEST_RESULTS = {}

# ISO 13485 요구사항 ID 데코레이터
def req_id(*ids):
    """
    데코레이터: 테스트 함수에 요구사항 ID를 연결합니다.
    이 데코레이터를 사용하여 각 테스트와 요구사항 간의 추적성을 확보합니다.
    
    사용 예:
    @pytest.mark.req_id("REQ-001", "REQ-002")
    def test_something():
        assert True
    """
    return pytest.mark.req_id(ids)

@pytest.fixture(scope="session")
def ensure_test_images():
    """Ensure required test images are present"""
    required_images = [
        "normal_chest_xray.jpg",
        "abnormal_chest_xray.jpg",
        "invalid_file.txt"
    ]
    
    missing_files = []
    for image in required_images:
        if not (TEST_DATA_DIR / image).exists():
            missing_files.append(image)
    
    if missing_files:
        pytest.fail(f"Required test files are missing: {', '.join(missing_files)}. "
                    f"Check README.md in {TEST_DATA_DIR} for instructions.")
    
    return True

@pytest.fixture(scope="session")
def api_server(ensure_test_images):
    """Start mock API server if not already running, or validate connection"""
    # First, check if the server is already running
    try:
        response = requests.get(f"{API_BASE_URL}/analyze/metadata")
        if response.status_code == 200:
            logger.info("API server already running - using existing instance")
            return API_BASE_URL
    except requests.exceptions.ConnectionError:
        logger.info("API server not detected - attempting to start server")
    
    # If not running, try to start it
    try:
        # Adjust paths based on your project structure
        server_dir = "../mock_server"
        server_process = subprocess.Popen(
            ["python", "app.py"],
            cwd=server_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start (max 10 seconds)
        max_wait = 10
        for i in range(max_wait):
            try:
                response = requests.get(f"{API_BASE_URL}/analyze/metadata")
                if response.status_code == 200:
                    logger.info(f"API server started successfully after {i+1} seconds")
                    break
            except requests.exceptions.ConnectionError:
                if i == max_wait - 1:
                    stdout, stderr = server_process.communicate(timeout=1)
                    logger.error(f"Server failed to start. Stdout: {stdout.decode()}, Stderr: {stderr.decode()}")
                    server_process.kill()
                    pytest.fail(f"Could not start API server after {max_wait} seconds")
                time.sleep(1)
        
        # Register finalizer to shut down server after tests
        def finalizer():
            logger.info("Shutting down API server")
            server_process.kill()
            server_process.wait()
        
        pytest.register_fixture_finalizer(id(server_process), finalizer)
        
    except Exception as e:
        logger.error(f"Failed to start API server: {str(e)}")
        pytest.fail(f"Could not start API server: {str(e)}")
    
    return API_BASE_URL

@pytest.fixture
def api_url(api_server):
    """Return the base API URL"""
    return f"{api_server}/analyze"

@pytest.fixture
def metadata_url(api_server):
    """Return the metadata API URL"""
    return f"{api_server}/analyze/metadata"

@pytest.fixture(scope="session")
def expected_model_info():
    """Returns expected model information for validation"""
    return {
        "version_pattern": r"^\d+\.\d+\.\d+$",
        "supported_modalities": ["X-Ray", "CT"],
        "min_sensitivity": 0.80,
        "min_specificity": 0.80
    }

@pytest.fixture
def sample_normal_image():
    """Return path to sample normal chest X-ray image"""
    image_path = TEST_DATA_DIR / "normal_chest_xray.jpg"
    if not image_path.exists():
        pytest.skip(f"Test image {image_path} not found")
    return str(image_path)

@pytest.fixture
def sample_abnormal_image():
    """Return path to sample abnormal chest X-ray image"""
    image_path = TEST_DATA_DIR / "abnormal_chest_xray.jpg"
    if not image_path.exists():
        pytest.skip(f"Test image {image_path} not found")
    return str(image_path)

@pytest.fixture
def invalid_file():
    """Return path to invalid file for testing error handling"""
    file_path = TEST_DATA_DIR / "invalid_file.txt"
    if not file_path.exists():
        pytest.skip(f"Test file {file_path} not found")
    return str(file_path)

# ISO 13485 요구사항 추적을 위한 플러그인
class RequirementTracePlugin:
    """
    테스트 결과를 캡처하여 요구사항 추적 정보를 생성하는 pytest 플러그인
    """
    def __init__(self, config):
        self.config = config
        self.requirement_results = {}
        self.test_to_req_map = {}
    
    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_protocol(self, item, nextitem):
        """테스트 시작 전 요구사항 ID 매핑 준비"""
        for marker in item.iter_markers(name="req_id"):
            req_ids = marker.args[0]
            for req_id in req_ids:
                if req_id not in self.requirement_results:
                    self.requirement_results[req_id] = {"tests": [], "status": "NotRun"}
                # 요구사항 ID와 테스트 이름 매핑 저장
                test_name = item.name
                self.test_to_req_map[test_name] = req_ids
                self.requirement_results[req_id]["tests"].append(test_name)
        
        yield
    
    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        """테스트 실행 후 결과를 요구사항 추적에 반영"""
        outcome = yield
        report = outcome.get_result()
        
        if report.when == "call":  # 테스트 실행 단계에서만 처리
            test_name = item.name
            if test_name in self.test_to_req_map:
                req_ids = self.test_to_req_map[test_name]
                for req_id in req_ids:
                    if report.passed:
                        if self.requirement_results[req_id]["status"] != "Failed":
                            self.requirement_results[req_id]["status"] = "Passed"
                    else:
                        self.requirement_results[req_id]["status"] = "Failed"
    
    def pytest_sessionfinish(self, session, exitstatus):
        """테스트 세션 종료 시 결과 저장"""
        global REQUIREMENT_TEST_RESULTS
        REQUIREMENT_TEST_RESULTS = self.requirement_results
        
        # JSON 파일로 결과 저장
        results_dir = Path(os.path.dirname(__file__)) / ".." / "scripts" / "temp"
        results_dir.mkdir(exist_ok=True, parents=True)
        
        with open(results_dir / "req_test_results.json", "w") as f:
            json.dump(self.requirement_results, f, indent=2)
        
        logger.info(f"요구사항 추적 결과가 저장되었습니다: {results_dir / 'req_test_results.json'}")


def pytest_configure(config):
    """pytest 설정 시 요구사항 추적 플러그인 등록"""
    # 요구사항 ID 마커 등록
    config.addinivalue_line("markers", "req_id(ids): ISO 13485 요구사항 추적을 위한 ID 매핑")
    
    # 플러그인 등록
    plugin = RequirementTracePlugin(config)
    config.pluginmanager.register(plugin, "requirement_trace_plugin") 