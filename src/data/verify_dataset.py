"""
Visualiza anotaciones YOLO sobre las imágenes para verificar la conversión.
Guarda las imágenes con bounding boxes en data/yolo/<split>/verified/.
"""

import random
from pathlib import Path

import cv2
import yaml


YOLO_DIR = Path("data/yolo")


def draw_boxes(img_path: Path, label_path: Path, out_path: Path):
    img = cv2.imread(str(img_path))
    if img is None:
        return
    h, w = img.shape[:2]

    if label_path.exists():
        for line in label_path.read_text().strip().splitlines():
            parts = line.split()
            _, cx, cy, bw, bh = map(float, parts)
            x1 = int((cx - bw / 2) * w)
            y1 = int((cy - bh / 2) * h)
            x2 = int((cx + bw / 2) * w)
            y2 = int((cy + bh / 2) * h)
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, "placa", (x1, y1 - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_path), img)


def verify_split(split: str, n_samples: int = 10):
    img_dir = YOLO_DIR / split / "images"
    lbl_dir = YOLO_DIR / split / "labels"
    out_dir = YOLO_DIR / split / "verified"

    images = list(img_dir.glob("*.jpg"))
    sample = random.sample(images, min(n_samples, len(images)))

    for img_path in sample:
        lbl_path = lbl_dir / f"{img_path.stem}.txt"
        out_path = out_dir / img_path.name
        draw_boxes(img_path, lbl_path, out_path)

    print(f"{split}: {len(sample)} imágenes verificadas → {out_dir}")


def print_stats():
    with open(YOLO_DIR / "data.yaml", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    print(f"Clases: {cfg['names']}")
    for split in ["train", "valid", "test"]:
        imgs = list((YOLO_DIR / split / "images").glob("*.jpg"))
        lbls = list((YOLO_DIR / split / "labels").glob("*.txt"))
        print(f"  {split}: {len(imgs)} imágenes, {len(lbls)} labels")


if __name__ == "__main__":
    print_stats()
    for split in ["train", "valid", "test"]:
        verify_split(split)
