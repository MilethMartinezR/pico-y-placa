"""
Pruebas de validación de formato de placa (sin cargar EasyOCR).
"""

import re
import pytest

PLATE_PATTERN = re.compile(r"^[A-Z]{3}\d{3}$|^[A-Z]{2}\d{2}[A-Z]$")


@pytest.mark.parametrize("plate", ["ABC123", "XYZ999", "AB12C", "ZZ00Z"])
def test_valid_plates(plate):
    assert PLATE_PATTERN.match(plate), f"Debería ser válida: {plate}"


@pytest.mark.parametrize("plate", ["AB123", "ABCD12", "123ABC", "AB1234", ""])
def test_invalid_plates(plate):
    assert not PLATE_PATTERN.match(plate), f"Debería ser inválida: {plate}"
