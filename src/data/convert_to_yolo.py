"""
Convierte anotaciones RetinaNet CSV a formato YOLO (txt por imagen).
CSV esperado: filename, x1, y1, x2, y2, class_name
"""

import csv
import shutil
from pathlib import Path


SPLITS = ["train", "valid", "test"]
RAW_DIR = Path("data/raw")
YOLO_DIR = Path("data/yolo")


def convert_split(split: str) -> int:
    csv_path = RAW_DIR / split / "_annotations.csv"
    src_img_dir = RAW_DIR / split
    dst_img_dir = YOLO_DIR / split / "images"
    dst_lbl_dir = YOLO_DIR / split / "labels"

    dst_img_dir.mkdir(parents=True, exist_ok=True)
    dst_lbl_dir.mkdir(parents=True, exist_ok=True)

    annotations: dict[str, list[tuple]] = {}

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or row[0].startswith("#"):
                continue
            # formato sin cabecera: filename, x1, y1, x2, y2, class
            if len(row) < 5:
                continue
            filename = row[0].strip()
            img_path = src_img_dir / filename
            if not img_path.exists():
                continue

            from PIL import Image
            with Image.open(img_path) as img:
                w, h = img.size

            x1, y1, x2, y2 = float(row[1]), float(row[2]), float(row[3]), float(row[4])

            cx = ((x1 + x2) / 2) / w
            cy = ((y1 + y2) / 2) / h
            bw = (x2 - x1) / w
            bh = (y2 - y1) / h

            cx = max(0.0, min(1.0, cx))
            cy = max(0.0, min(1.0, cy))
            bw = max(0.0, min(1.0, bw))
            bh = max(0.0, min(1.0, bh))

            annotations.setdefault(filename, []).append((cx, cy, bw, bh))

    count = 0
    for filename, boxes in annotations.items():
        stem = Path(filename).stem
        shutil.copy2(src_img_dir / filename, dst_img_dir / filename)

        label_path = dst_lbl_dir / f"{stem}.txt"
        with open(label_path, "w") as f:
            for cx, cy, bw, bh in boxes:
                f.write(f"0 {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}\n")
        count += 1

    return count


def write_data_yaml():
    yaml_path = YOLO_DIR / "data.yaml"
    train_count = sum(1 for _ in (YOLO_DIR / "train" / "images").glob("*.jpg"))
    valid_count = sum(1 for _ in (YOLO_DIR / "valid" / "images").glob("*.jpg"))

    content = f"""\
path: {YOLO_DIR.resolve()}
train: train/images
val: valid/images
test: test/images

nc: 1
names:
  - placa
"""
    yaml_path.write_text(content, encoding="utf-8")
    print(f"data.yaml escrito — train: {train_count}, valid: {valid_count}")


def main():
    for split in SPLITS:
        n = convert_split(split)
        print(f"{split}: {n} imágenes convertidas")
    write_data_yaml()
    print("Conversión completa.")


if __name__ == "__main__":
    main()
