"""
Verifica que la conversión CSV → YOLO produce coordenadas normalizadas válidas.
"""

import csv
import tempfile
from pathlib import Path

import pytest


def csv_to_yolo_row(x1, y1, x2, y2, img_w, img_h):
    cx = ((x1 + x2) / 2) / img_w
    cy = ((y1 + y2) / 2) / img_h
    bw = (x2 - x1) / img_w
    bh = (y2 - y1) / img_h
    return cx, cy, bw, bh


def test_normalized_values_in_range():
    cx, cy, bw, bh = csv_to_yolo_row(50, 100, 200, 150, 416, 416)
    for v in (cx, cy, bw, bh):
        assert 0.0 <= v <= 1.0, f"Valor fuera de rango: {v}"


def test_center_calculation():
    cx, cy, bw, bh = csv_to_yolo_row(0, 0, 416, 416, 416, 416)
    assert cx == pytest.approx(0.5)
    assert cy == pytest.approx(0.5)
    assert bw == pytest.approx(1.0)
    assert bh == pytest.approx(1.0)


def test_small_box():
    cx, cy, bw, bh = csv_to_yolo_row(100, 200, 150, 220, 416, 416)
    assert bw == pytest.approx(50 / 416)
    assert bh == pytest.approx(20 / 416)
