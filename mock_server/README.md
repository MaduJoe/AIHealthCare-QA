# 의료 AI 진단 모델 서버

이 서버는 의료 이미지 분석을 위한 AI 모델을 호스팅합니다.

## 기능

- 의료 이미지 분석 및 분류
- 9가지 클래스에 대한 이미지 분류 모델 (ADI, BACK, DEB, LYM, MUC, MUS, NORM, STR, TUM)
- 이미지 분석 결과에 기반한 위험 점수 및 플래그 제공
- Hugging Face Transformers 기반 이미지 분류
- 직관적인 API를 통한 이미지 분석 리포트

## 설치 및 실행

### 환경 설정

1. Python 3.8 이상 설치
2. 필요한 패키지 설치:

```bash
pip install -r requirements.txt
```

3. 필요한 라이브러리:
   - Flask
   - Transformers
   - PyTorch
   - Pillow

### 서버 실행

```bash
python app.py
```

## API 엔드포인트

### 1. 이미지 분석 `/analyze` (POST)

의료 이미지를 분석하고 결과를 반환합니다.

**요청 본문:**
- 멀티파트 폼: `file` 필드에 이미지 파일 (PNG, JPG, JPEG)

**응답:**
```json
{
  "status": "success",
  "model_type": "huggingface",
  "processing_time_ms": 456.23,
  "result": {
    "abnormality_score": 75,
    "confidence": "0.75",
    "flags": ["class_name"]
  }
}
```

## 모델 정보

- 기본 모델: `google/vit-base-patch16-224` (Hugging Face 모델)
- 모델 유형: Vision Transformer (ViT)
- 이미지 분류: 9개 클래스 분류
  - ADI: 지방조직
  - BACK: 배경
  - DEB: 파편
  - LYM: 림프구
  - MUC: 점액
  - MUS: 근육
  - NORM: 정상
  - STR: 간질
  - TUM: 종양

## 사용자 인터페이스 (UI 앱)

서버는 `ui_app.py`로 구현된 Streamlit 기반 웹 인터페이스와 함께 사용할 수 있습니다:

- 이미지 업로드 및 분석 요청
- 분석 결과 시각화
- 환자 정보 등록 및 관리
- 분석 결과 보고서 생성 및 다운로드
- 이메일을 통한 결과 공유 시뮬레이션

## 알려진 제한사항

- PNG, JPG, JPEG 이미지 형식만 지원합니다.
- 모델은 연구용(RUO)으로, 의료 진단 목적으로 직접 사용하면 안 됩니다. 