"""
Orquesta los 3 pasos: detección → OCR → reglas.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

from src.model.detect_plate import PlateDetector
from src.model.read_plate import read_plate
from src.rules.pico_placa_engine import PicoPlacaResult, check


@dataclass
class PipelineResult:
    success: bool
    plate: str | None
    restriction: PicoPlacaResult | None
    error: str | None


_detector: PlateDetector | None = None


def _get_detector() -> PlateDetector:
    global _detector
    if _detector is None:
        _detector = PlateDetector()
    return _detector


def run(
    image: np.ndarray,
    city: str,
    at: datetime | None = None,
) -> PipelineResult:
    """
    image : BGR numpy array
    city  : clave de ciudad ('bogota', 'medellin', 'cali')
    at    : timestamp de consulta (None = ahora)
    """
    detector = _get_detector()

    crop = detector.detect(image)
    if crop is None:
        return PipelineResult(False, None, None, "No se detectó ninguna placa en la imagen")

    plate = read_plate(crop)
    if plate is None:
        return PipelineResult(False, None, None, "Placa detectada pero no legible")

    try:
        result = check(plate, city, at)
    except ValueError as e:
        return PipelineResult(False, plate, None, str(e))

    return PipelineResult(True, plate, result, None)


def run_from_file(image_path: str | Path, city: str) -> PipelineResult:
    img = cv2.imread(str(image_path))
    if img is None:
        return PipelineResult(False, None, None, f"No se pudo abrir la imagen: {image_path}")
    return run(img, city)
