import warnings
warnings.filterwarnings("ignore", "Glyph \d+ .* missing from font.*")
import requests
import json
import time
import os
import pytest
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
import matplotlib as mpl

# 한글 폰트 설정
# Windows의 경우
if os.name == 'nt':
    # 맑은 고딕 폰트 사용
    # font_path = r'C:\Windows\Fonts\malgun.ttf'
    font_path = r'C:\Windows\Fonts\Arial\arial.ttf'
    if os.path.exists(font_path):
        font_prop = mpl.font_manager.FontProperties(fname=font_path)
        mpl.rcParams['font.family'] = font_prop.get_name()
    else:
        # 맑은 고딕 폰트가 없는 경우 기본 폰트 사용
        mpl.rcParams['font.family'] = 'sans-serif'
        mpl.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
else:
    # Linux/Mac의 경우
    mpl.rcParams['font.family'] = 'sans-serif'
    mpl.rcParams['font.sans-serif'] = ['NanumGothic', 'NanumBarunGothic', 'Malgun Gothic', 'Arial', 'Helvetica']

# 경고 필터 설정 (선택사항)
import warnings
warnings.filterwarnings("ignore", "Glyph \d+ .* missing from font.*")
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")

API_URL = "http://localhost:5000/analyze"
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "test_data")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "performance_results")

# 결과 디렉토리가 없으면 생성
os.makedirs(RESULTS_DIR, exist_ok=True)

def get_test_images():
    """테스트 데이터 디렉토리에서 이미지 파일 목록 가져오기"""
    return [
        os.path.join(TEST_DATA_DIR, f) 
        for f in os.listdir(TEST_DATA_DIR)
        if f.endswith(('.jpg', '.png', '.jpeg'))
    ]

def make_api_call(file_path):
    """API 호출 및 응답 시간 측정"""
    try:
        start_time = time.time()
        with open(file_path, "rb") as f:
            response = requests.post(API_URL, files={"file": f})
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            processing_time_ms = data.get("processing_time_ms", 0)
            return {
                "status_code": response.status_code,
                "response_time": (end_time - start_time) * 1000,  # 밀리초 단위로 변환
                "processing_time_ms": processing_time_ms,
                "file_size": os.path.getsize(file_path) / 1024  # KB 단위로 변환
            }
        else:
            return {
                "status_code": response.status_code,
                "response_time": (end_time - start_time) * 1000,
                "processing_time_ms": 0,
                "file_size": os.path.getsize(file_path) / 1024
            }
    except Exception as e:
        print(f"Error making API call with {file_path}: {str(e)}")
        return {
            "status_code": 0,
            "response_time": 0,
            "processing_time_ms": 0,
            "file_size": 0,
            "error": str(e)
        }

def test_baseline_performance():
    """기본 성능 테스트 - 단일 이미지 처리 시간 측정"""
    images = get_test_images()
    if not images:
        pytest.skip("테스트 이미지가 없습니다")
    
    sample_image = images[0]
    result = make_api_call(sample_image)
    
    # 응답이 성공인지 확인
    assert result["status_code"] == 200, f"API 호출 실패: {result.get('error', '')}"
    
    # 응답 시간이 기준치 이내인지 확인 (3초)
    assert result["response_time"] < 3000, f"API 응답 시간이 너무 깁니다: {result['response_time']:.2f}ms"
    
    # 결과 출력
    print(f"\n기본 성능 테스트 결과:")
    print(f"이미지 크기: {result['file_size']:.2f} KB")
    print(f"응답 시간: {result['response_time']:.2f} ms")
    print(f"서버 처리 시간: {result['processing_time_ms']:.2f} ms")

def test_concurrent_load():
    """동시 부하 테스트 - 다수의 동시 요청 처리"""
    images = get_test_images()
    if len(images) < 3:
        pytest.skip("충분한 테스트 이미지가 없습니다")
    
    # 동시에 처리할 요청 수 (최대 10개, 이미지 수에 따라 조절)
    concurrent_requests = min(10, len(images))
    
    print(f"\n{concurrent_requests}개의 동시 요청으로 부하 테스트 시작...")
    
    results = []
    with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
        # 각 이미지에 대해 API 호출 함수 실행
        futures = [executor.submit(make_api_call, img) for img in images[:concurrent_requests]]
        # 결과 수집
        for future in tqdm(as_completed(futures), total=len(futures), desc="Processing concurrent requests"):
            results.append(future.result())
    
    # 성공한 요청 수 확인
    successful_requests = sum(1 for r in results if r["status_code"] == 200)
    
    assert successful_requests == concurrent_requests, \
        f"동시 요청 중 일부 실패: {successful_requests}/{concurrent_requests} 성공"
    
    # 결과 통계 계산
    response_times = [r["response_time"] for r in results]
    processing_times = [r["processing_time_ms"] for r in results]
    
    avg_response_time = statistics.mean(response_times)
    max_response_time = max(response_times)
    avg_processing_time = statistics.mean(processing_times)
    
    print(f"\n동시 부하 테스트 결과 (요청 수: {concurrent_requests}):")
    print(f"평균 응답 시간: {avg_response_time:.2f} ms")
    print(f"최대 응답 시간: {max_response_time:.2f} ms")
    print(f"서버 평균 처리 시간: {avg_processing_time:.2f} ms")
    
    # 응답 시간에 대한 시각화 저장
    plt.figure(figsize=(10, 6))
    plt.bar(range(len(response_times)), response_times)
    plt.xlabel('Request Number')
    plt.ylabel('Response Time (ms)')
    plt.title(f'Concurrent Requests ({concurrent_requests}) Response Times')
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(RESULTS_DIR, 'concurrent_response_times.png'))

@pytest.mark.skip(reason="장시간 실행되는 부하 테스트는 필요할 때만 실행")
def test_extended_load():
    """확장 부하 테스트 - 다양한 수준의 동시 요청 처리"""
    images = get_test_images()
    if len(images) < 5:
        pytest.skip("충분한 테스트 이미지가 없습니다")
    
    # 테스트할 동시 요청 수준 (1, 5, 10, 15, 20)
    concurrency_levels = [1, 5, 10, 15, 20]
    avg_times = []
    max_times = []
    
    for concurrency in concurrency_levels:
        # 사용 가능한 이미지 수에 맞게 조정
        actual_concurrency = min(concurrency, len(images))
        if actual_concurrency < concurrency:
            print(f"경고: 요청된 동시성 {concurrency}를 위한 충분한 이미지가 없습니다. {actual_concurrency}로 조정합니다.")
        
        results = []
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=actual_concurrency) as executor:
            # 현재 동시성 수준에 맞게 이미지 선택
            selected_images = images[:actual_concurrency]
            
            # 각 이미지에 대해 API 호출 함수 실행
            futures = [executor.submit(make_api_call, img) for img in selected_images]
            # 결과 수집
            for future in as_completed(futures):
                results.append(future.result())
        
        response_times = [r["response_time"] for r in results if r["status_code"] == 200]
        
        if response_times:
            avg_time = statistics.mean(response_times)
            max_time = max(response_times)
            avg_times.append(avg_time)
            max_times.append(max_time)
            
            print(f"동시성 수준 {actual_concurrency}: 평균 {avg_time:.2f}ms, 최대 {max_time:.2f}ms")
        else:
            print(f"동시성 수준 {actual_concurrency}: 모든 요청 실패")
            avg_times.append(0)
            max_times.append(0)
    
    # 결과를 그래프로 시각화
    x = np.array(concurrency_levels[:len(avg_times)])
    
    plt.figure(figsize=(12, 7))
    plt.plot(x, avg_times, 'o-', label='Average Response Time')
    plt.plot(x, max_times, 's-', label='Maximum Response Time')
    plt.xlabel('Number of Concurrent Requests')
    plt.ylabel('Response Time (ms)')
    plt.title('API Response Time by Concurrency Level')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(RESULTS_DIR, 'scalability_test.png'))

def test_response_time_vs_filesize():
    """파일 크기와 응답 시간 관계 분석"""
    images = get_test_images()
    if len(images) < 3:
        pytest.skip("충분한 테스트 이미지가 없습니다")
    
    results = []
    for image in tqdm(images, desc="Analyzing response time by file size"):
        results.append(make_api_call(image))
    
    # 성공한 요청만 필터링
    successful_results = [r for r in results if r["status_code"] == 200]
    
    if len(successful_results) < 3:
        pytest.skip("충분한 성공한 요청이 없습니다")
    
    file_sizes = [r["file_size"] for r in successful_results]
    response_times = [r["response_time"] for r in successful_results]
    
    # 산점도 그래프로 시각화
    plt.figure(figsize=(10, 6))
    plt.scatter(file_sizes, response_times)
    
    # 추세선 추가
    z = np.polyfit(file_sizes, response_times, 1)
    p = np.poly1d(z)
    plt.plot(file_sizes, p(file_sizes), "r--", alpha=0.8)
    
    plt.xlabel('File Size (KB)')
    plt.ylabel('Response Time (ms)')
    plt.title('Relationship between File Size and API Response Time')
    plt.grid(True, alpha=0.3)
    
    # 상관관계 계산
    correlation = np.corrcoef(file_sizes, response_times)[0, 1]
    plt.annotate(f'Correlation: {correlation:.2f}', 
                xy=(0.05, 0.95), 
                xycoords='axes fraction')
    
    plt.savefig(os.path.join(RESULTS_DIR, 'filesize_vs_responsetime.png'))
    
    print(f"\n파일 크기와 응답 시간 분석:")
    print(f"파일 크기 범위: {min(file_sizes):.2f} ~ {max(file_sizes):.2f} KB")
    print(f"응답 시간 범위: {min(response_times):.2f} ~ {max(response_times):.2f} ms")
    print(f"상관계수: {correlation:.2f}") 