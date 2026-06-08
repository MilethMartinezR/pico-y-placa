"""
Entrena YOLOv8s para detección de placas colombianas.
Ejecutar en Google Colab (GPU T4) o localmente con CUDA.

Uso:
    python src/model/train_detector.py
"""

from pathlib import Path
from ultralytics import YOLO


DATA_YAML = Path("data/yolo/data.yaml").resolve()
WEIGHTS_DIR = Path("models/detector/weights")
BASE_MODEL = "yolov8s.pt"

EPOCHS = 100
IMG_SIZE = 416
BATCH = 16
PATIENCE = 20


def train():
    WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)

    model = YOLO(BASE_MODEL)

    results = model.train(
        data=str(DATA_YAML),
        epochs=EPOCHS,
        imgsz=IMG_SIZE,
        batch=BATCH,
        patience=PATIENCE,
        project="models/detector",
        name="run",
        exist_ok=True,
        augment=True,
        degrees=5.0,
        translate=0.1,
        scale=0.3,
        fliplr=0.0,
        mosaic=0.5,
        hsv_h=0.015,
        hsv_s=0.5,
        hsv_v=0.3,
    )

    best = Path(results.save_dir) / "weights" / "best.pt"
    last = Path(results.save_dir) / "weights" / "last.pt"

    if best.exists():
        import shutil
        shutil.copy2(best, WEIGHTS_DIR / "best.pt")
        shutil.copy2(last, WEIGHTS_DIR / "last.pt")
        print(f"Pesos guardados en {WEIGHTS_DIR}")

    print(f"mAP50: {results.results_dict.get('metrics/mAP50(B)', 'N/A')}")


if __name__ == "__main__":
    train()
