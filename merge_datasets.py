import json
import os
import cv2

COCO_JSON = "coco_dataset/train/_annotations.coco.json"
COCO_IMAGES_DIR = "coco_dataset/train"
OUTPUT_DIR = "polish-dataset/classification"
COCO_TO_FOLDER = {
    "30": "B33",
    "40": "B33",
    "50": "B33",
    "60": "B33",
    "70": "B33",
    "stop": "B20",
    "zakaz_wjazdu": "B2",
    "Zakaz_wyprzedzania": "B23",
    "Zakaz_zatrzymywania": "B36",
    "przejscie": "D6",
    "uwaga_dzieci": "A17",
    "prog": "A30",
    "niebezpieczenstwo": "A30",
    "pierwszenstwo": "D1",
    "ustap": "other",
    "zwierzyna": "other",
    "koniec": "other",
    "koniec_pierwszenstwa": "other",
    "Roboty_drogowe": "other",
    "Road-signs": None,
}
MIN_CROP_SIZE = 64


def main():
    with open(COCO_JSON) as f:
        data = json.load(f)
    id_to_filename = {img["id"]: img["file_name"] for img in data["images"]}
    id_to_name = {cat["id"]: cat["name"] for cat in data["categories"]}
    counters = {folder: 0 for folder in set(COCO_TO_FOLDER.values()) if folder}
    skipped_small = 0
    skipped_generic = 0
    for ann in data["annotations"]:
        cat_name = id_to_name[ann["category_id"]]
        folder = COCO_TO_FOLDER.get(cat_name)
        if folder is None:
            skipped_generic += 1
            continue
        img_path = os.path.join(COCO_IMAGES_DIR, id_to_filename[ann["image_id"]])
        if not os.path.exists(img_path):
            print(f"  [WARN] Image not found: {img_path}")
            continue
        img = cv2.imread(img_path)
        if img is None:
            continue
        x, y, w, h = [round(float(v)) for v in ann["bbox"]]
        if w < MIN_CROP_SIZE or h < MIN_CROP_SIZE:
            skipped_small += 1
            continue
        ih, iw = img.shape[:2]
        x1 = max(0, x)
        y1 = max(0, y)
        x2 = min(iw, x + w)
        y2 = min(ih, y + h)
        crop = img[y1:y2, x1:x2]
        if crop.size == 0:
            continue
        dest_dir = os.path.join(OUTPUT_DIR, folder)
        os.makedirs(dest_dir, exist_ok=True)
        filename = f"coco_{ann['id']}.jpg"
        cv2.imwrite(os.path.join(dest_dir, filename), crop)
        counters[folder] += 1
    print("\n=== Merge complete ===")
    print(f"Skipped (generic 'Road-signs' class): {skipped_generic}")
    print(f"Skipped (crop < {MIN_CROP_SIZE}px): {skipped_small}")
    print("\nImages added per class:")
    total = 0
    for folder, count in sorted(counters.items()):
        if count > 0:
            print(f"  {folder}: +{count}")
            total += count
    print(f"\nTotal added: {total} images")


if __name__ == "__main__":
    main()
