"""
Detecta y recorta la región de la placa en una imagen usando YOLOv8.
"""

from pathlib import Path

import numpy as np
from ultralytics import YOLO


WEIGHTS = Path("models/detector/weights/best.pt")
CONF_THRESHOLD = 0.45


class PlateDetector:
    def __init__(self, weights: Path = WEIGHTS):
        if not weights.exists():
            raise FileNotFoundError(f"Pesos no encontrados: {weights}")
        self.model = YOLO(str(weights))

    def detect(self, image: np.ndarray) -> np.ndarray | None:
        """
        Recibe una imagen BGR (numpy array) y retorna el recorte de la placa
        con mayor confianza, o None si no se detecta ninguna.
        """
        results = self.model(image, conf=CONF_THRESHOLD, verbose=False)[0]

        if len(results.boxes) == 0:
            return None

        best = max(results.boxes, key=lambda b: float(b.conf))
        x1, y1, x2, y2 = map(int, best.xyxy[0].tolist())

        # margen pequeño para no cortar caracteres en el borde
        h, w = image.shape[:2]
        pad = 4
        x1 = max(0, x1 - pad)
        y1 = max(0, y1 - pad)
        x2 = min(w, x2 + pad)
        y2 = min(h, y2 + pad)

        return image[y1:y2, x1:x2]
