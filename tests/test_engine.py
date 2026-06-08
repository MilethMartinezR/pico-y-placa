"""
Pruebas del motor de reglas. No requieren modelos ML.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from src.rules.pico_placa_engine import check

BOG = ZoneInfo("America/Bogota")


def dt(weekday: int, hour: int, minute: int = 0) -> datetime:
    """Construye un datetime en zona Bogotá con el día de la semana indicado (0=lunes)."""
    from datetime import date, timedelta
    # semana de referencia sin festivos: 2024-01-08 (lunes)
    base = date(2024, 1, 8)
    d = base + timedelta(days=weekday)
    return datetime(d.year, d.month, d.day, hour, minute, tzinfo=BOG)


# ── Bogotá en horario pico ────────────────────────────────────────────────────

def test_restricted_bogota_monday_digit1():
    result = check("ABC121", "bogota", at=dt(0, 7))  # lunes 7am, dígito 1
    assert result.restricted is True

def test_restricted_bogota_friday_digit0():
    result = check("XYZ990", "bogota", at=dt(4, 16))  # viernes 4pm, dígito 0
    assert result.restricted is True

def test_not_restricted_bogota_wrong_digit():
    result = check("ABC123", "bogota", at=dt(0, 7))  # lunes 7am, dígito 3 (no restringido)
    assert result.restricted is False

# ── Fuera de horario pico ─────────────────────────────────────────────────────

def test_no_restriction_outside_peak():
    result = check("ABC121", "bogota", at=dt(0, 12))  # lunes 12pm
    assert result.restricted is False

def test_no_restriction_weekend():
    result = check("ABC121", "bogota", at=dt(5, 7))  # sábado 7am
    assert result.restricted is False

# ── Ciudad no soportada ───────────────────────────────────────────────────────

def test_unsupported_city():
    with pytest.raises(ValueError, match="Ciudad no soportada"):
        check("ABC123", "bucaramanga")

# ── Festivo ───────────────────────────────────────────────────────────────────

def test_no_restriction_on_holiday():
    # 1 enero 2024 es festivo en Colombia (Año Nuevo), martes
    holiday = datetime(2024, 1, 1, 7, 30, tzinfo=BOG)
    result = check("ABC123", "bogota", at=holiday)
    assert result.restricted is False
