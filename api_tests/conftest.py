import pytest
import requests
import subprocess
import time
import os
import logging
# from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define test constants
API_BASE_URL = "http://localhost:5000"
# TEST_DATA_DIR = Path("api_tests/test_data")
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "test_data")  # 동적 절대 경로 방식


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