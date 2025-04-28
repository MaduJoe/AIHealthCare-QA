"""
DICOM 파일 처리 모듈

이 모듈은 DICOM 의료 이미지 파일을 처리하기 위한 기능을 제공합니다.
"""

import io
import logging
import numpy as np
from PIL import Image
import pydicom
from pydicom.errors import InvalidDicomError

logger = logging.getLogger(__name__)

def is_dicom_file(file_bytes):
    """
    바이트 데이터가 DICOM 형식인지 확인
    
    Args:
        file_bytes: 이미지 파일 바이트 데이터
        
    Returns:
        DICOM 파일 여부 (bool)
    """
    try:
        with io.BytesIO(file_bytes) as fp:
            pydicom.dcmread(fp, stop_before_pixels=True)
        return True
    except (InvalidDicomError, Exception):
        return False

def dicom_to_pil(dicom_bytes):
    """
    DICOM 바이트 데이터를 PIL Image로 변환
    
    Args:
        dicom_bytes: DICOM 파일 바이트 배열
    
    Returns:
        PIL Image 객체와 메타데이터 딕셔너리
    """
    try:
        with io.BytesIO(dicom_bytes) as fp:
            ds = pydicom.dcmread(fp)
        
        # 픽셀 데이터 추출
        pixel_array = ds.pixel_array
        
        # 16비트 이미지 처리 (일반적인 의료 영상)
        if pixel_array.dtype == np.uint16:
            max_val = np.max(pixel_array)
            if max_val > 0:
                # 8비트 스케일링 (0-255)
                scaled_array = (pixel_array / max_val * 255).astype(np.uint8)
            else:
                scaled_array = pixel_array.astype(np.uint8)
        else:
            scaled_array = pixel_array.astype(np.uint8)
        
        # 단일 채널이면 RGB로 변환
        if len(scaled_array.shape) == 2:
            img = Image.fromarray(scaled_array, mode='L').convert('RGB')
        else:
            img = Image.fromarray(scaled_array)
        
        # 메타데이터 추출
        metadata = {
            'patient_id': getattr(ds, 'PatientID', 'Unknown'),
            'patient_name': str(getattr(ds, 'PatientName', 'Unknown')),
            'study_date': getattr(ds, 'StudyDate', 'Unknown'),
            'modality': getattr(ds, 'Modality', 'Unknown'),
            'manufacturer': getattr(ds, 'Manufacturer', 'Unknown')
        }
        
        logger.info(f"DICOM 파일 변환 완료: {metadata['modality']} 이미지")
        return img, metadata
    
    except Exception as e:
        logger.error(f"DICOM 파일 변환 실패: {str(e)}")
        raise ValueError(f"DICOM 파일 변환 중 오류 발생: {str(e)}")

def extract_dicom_metadata(dicom_bytes):
    """
    DICOM 파일에서 메타데이터만 추출
    
    Args:
        dicom_bytes: DICOM 파일 바이트 배열
        
    Returns:
        메타데이터 딕셔너리
    """
    try:
        with io.BytesIO(dicom_bytes) as fp:
            ds = pydicom.dcmread(fp, stop_before_pixels=True)
        
        # 공통 DICOM 태그 추출
        metadata = {
            'patient_id': getattr(ds, 'PatientID', 'Unknown'),
            'patient_name': str(getattr(ds, 'PatientName', 'Unknown')),
            'study_date': getattr(ds, 'StudyDate', 'Unknown'),
            'study_time': getattr(ds, 'StudyTime', 'Unknown'),
            'modality': getattr(ds, 'Modality', 'Unknown'),
            'body_part': getattr(ds, 'BodyPartExamined', 'Unknown'),
            'manufacturer': getattr(ds, 'Manufacturer', 'Unknown'),
            'institution': getattr(ds, 'InstitutionName', 'Unknown')
        }
        
        return metadata
    except Exception as e:
        logger.error(f"DICOM 메타데이터 추출 실패: {str(e)}")
        return {"error": str(e)} 