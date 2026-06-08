"""
Lee el texto de la placa a partir de un recorte usando EasyOCR.
Valida el resultado contra el formato oficial colombiano.
"""

import re

import cv2
import easyocr
import numpy as np


# ABC123 (motos/carros antiguos) o AB12C (formato actual)
PLATE_PATTERN = re.compile(r"[A-Z]{3}\d{3}|[A-Z]{2}\d{2}[A-Z]|[A-Z]{2,3}\d{3}")

_reader: easyocr.Reader | None = None


def _get_reader() -> easyocr.Reader:
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(["es", "en"], gpu=False)
    return _reader


def _preprocess(crop: np.ndarray) -> list[np.ndarray]:
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return [thresh, cv2.bitwise_not(thresh), gray]


def read_plate(crop: np.ndarray) -> str | None:
    """
    Retorna la cadena de la placa (ej. "ABC123") o None si no pasa validación.
    """
    variants = _preprocess(crop)
    reader = _get_reader()

    # intenta cada variante de preprocesado + imagen original
    for i, img in enumerate([*variants, crop]):
        results = reader.readtext(img, detail=0, paragraph=False)
        raw = "".join(results).upper().replace(" ", "").replace("-", "")
        raw = re.sub(r"[^A-Z0-9]", "", raw)
        print(f"[OCR] variante {i}: '{raw}'")
        m = PLATE_PATTERN.search(raw)
        if m:
            return m.group()

    return None
