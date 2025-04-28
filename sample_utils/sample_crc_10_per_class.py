from PIL import Image
import io

from datasets import load_dataset
import os
from tqdm import tqdm

# 1. 스트리밍 모드로 데이터셋 로드
print("Loading NCT-CRC-HE dataset in streaming mode...")
# dataset = load_dataset("1aurent/NCT-CRC-HE", split="train", streaming=True)

dataset = load_dataset(
    "1aurent/NCT-CRC-HE",
    # split="NCT_CRC_HE_100K",  # ✅ 여기 수정!!
    split="CRC_VAL_HE_7K",  # ✅ 여기 수정!!
    streaming=True
)

# 2. 타겟 클래스 정의
target_classes = ["ADI", "BACK", "DEB", "LYM", "MUC", "MUS", "NORM", "STR", "TUM"]


# Label ID -> Label Name 매핑
label_id_to_name = {
    0: "ADI",
    1: "BACK",
    2: "DEB",
    3: "LYM",
    4: "MUC",
    5: "MUS",
    6: "NORM",
    7: "STR",
    8: "TUM"
}

# 3. 출력 디렉토리 생성
output_dir = "sampled_crc_images"
os.makedirs(output_dir, exist_ok=True)

# 4. 클래스별 저장 카운터 초기화
class_counters = {cls: 0 for cls in target_classes}
max_per_class = 10  # 클래스당 최대 10장 저장

# 5. 데이터셋 순회하며 샘플링
print("Sampling images...")

for example in tqdm(dataset):
    label_id = example['label']
    label = label_id_to_name[label_id]  # 🛠 여기 추가
    
    if label in target_classes and class_counters[label] < max_per_class:
        # 클래스별 폴더 생성
        class_dir = os.path.join(output_dir, label)
        os.makedirs(class_dir, exist_ok=True)
        
        # ✅ 수정: 스트리밍에서는 binary로 이미지 열기
        image_bytes = example['image']
        if isinstance(image_bytes, bytes):
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        else:
            image = example['image']
        
        # 이미지 저장
        img_filename = f"{class_counters[label]}.png"
        img_path = os.path.join(class_dir, img_filename)
        image.save(img_path)
        
        # 카운터 증가
        class_counters[label] += 1
    
    if all(count >= max_per_class for count in class_counters.values()):
        break

        