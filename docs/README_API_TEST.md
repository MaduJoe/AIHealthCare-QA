# 📘 LunitCare QA API 레퍼런스 - API 명세

본 문서는 LunitCare QA 시스템의 API 엔드포인트를 정리한 레퍼런스입니다.

## 기본 정보

- **기본 URL**: `http://localhost:5000`
- **콘텐츠 타입**: `multipart/form-data`, `application/json`
- **응답 형식**: JSON

## 엔드포인트 목록

### 1. 이미지 분석 API

#### POST /analyze

의료 이미지를 분석하여 분류 결과와 비정상 점수를 반환합니다.

**요청**

```
POST /analyze
Content-Type: multipart/form-data
```

**매개변수**

| 이름 | 타입 | 필수 | 설명 |
|------|------|------|------|
| file | 파일 | Y | 분석할 의료 이미지 파일 (PNG, JPG, JPEG) |

**응답**

```json
{
  "status": "success",
  "model_type": "huggingface",
  "processing_time_ms": 456.23,
  "result": {
    "abnormality_score": 75,
    "confidence": "0.75",
    "flags": ["TUM"]
  }
}
```

**응답 필드 설명**

| 필드 | 타입 | 설명 |
|------|------|------|
| status | 문자열 | 요청 처리 상태 ("success" 또는 "error") |
| model_type | 문자열 | 분석에 사용된 모델 유형 |
| processing_time_ms | 숫자 | 처리 시간(밀리초) |
| result | 객체 | 분석 결과 |
| result.abnormality_score | 숫자 | 이상 점수 (0-100) |
| result.confidence | 문자열 | 예측 신뢰도 |
| result.flags | 배열 | 발견된 이상 항목 목록 |

**오류 응답**

```json
{
  "status": "error",
  "message": "No file uploaded",
  "details": "파일이 없습니다"
}
```

**상태 코드**

| 코드 | 설명 |
|------|------|
| 200 | 성공 |
| 400 | 잘못된 요청 (파일 누락, 지원되지 않는 파일 형식 등) |
| 500 | 서버 오류 |

### 2. 의료 AI 모델 정보

#### GET /model_info

의료 AI 모델에 대한 상세 정보를 제공합니다.

**요청**

```
GET /model_info
```

**응답**

```json
{
  "model_name": "google/vit-base-patch16-224",
  "model_type": "Vision Transformer",
  "num_classes": 9,
  "classes": ["ADI", "BACK", "DEB", "LYM", "MUC", "MUS", "NORM", "STR", "TUM"],
  "class_descriptions": {
    "ADI": "지방조직",
    "BACK": "배경",
    "DEB": "파편",
    "LYM": "림프구",
    "MUC": "점액",
    "MUS": "근육",
    "NORM": "정상",
    "STR": "간질",
    "TUM": "종양"
  },
  "version": "1.0"
}
```

## 에러 코드 및 메시지

| 코드 | 설명 |
|------|------|
| INVALID_FILE | 유효하지 않은 파일 형식 |
| NO_FILE | 파일이 제공되지 않음 |
| PROCESSING_ERROR | 이미지 처리 중 오류 발생 |
| MODEL_ERROR | 모델 추론 중 오류 발생 |

## 사용 예시

### cURL을 사용한 이미지 분석 요청

```bash
curl -X POST \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_image.jpg" \
  http://localhost:5000/analyze
```

### Python requests 라이브러리를 사용한 예시

```python
import requests

url = "http://localhost:5000/analyze"
files = {"file": open("sample_image.jpg", "rb")}

response = requests.post(url, files=files)
result = response.json()

print(result)
```

## 참고사항

- 이미지 파일 크기는 10MB 이하로 제한됩니다.
- 지원되는 이미지 형식: JPG, JPEG, PNG
- 분석 결과는 캐시되지 않으며 매 요청마다 새로운 분석이 수행됩니다. 