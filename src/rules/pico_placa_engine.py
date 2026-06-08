"""
Motor de decisión de Pico y Placa.

Uso:
    from src.rules.pico_placa_engine import check
    result = check("ABC123", "bogota")
"""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .holidays import is_holiday


RULES_PATH = Path(__file__).parent / "restrictions.json"
DAY_MAP = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


@dataclass
class PicoPlacaResult:
    plate: str
    city: str
    city_name: str
    restricted: bool
    reason: str
    checked_at: str


def _load_rules() -> dict:
    with open(RULES_PATH, encoding="utf-8") as f:
        return json.load(f)


def check(plate: str, city: str, at: datetime | None = None) -> PicoPlacaResult:
    """
    Determina si la placa tiene restricción en la ciudad y momento dados.
    Si `at` es None, usa la hora actual en la zona horaria de la ciudad.
    """
    rules = _load_rules()

    city = city.lower().strip()
    if city not in rules:
        raise ValueError(f"Ciudad no soportada: '{city}'. Disponibles: {list(rules.keys())}")

    cfg = rules[city]
    tz = ZoneInfo(cfg["timezone"])

    now = at.astimezone(tz) if at else datetime.now(tz)

    checked_at = now.strftime("%Y-%m-%d %H:%M:%S %Z")
    day_name = DAY_MAP[now.weekday()]

    def _no_restriction(reason: str) -> PicoPlacaResult:
        return PicoPlacaResult(plate, city, cfg["name"], False, reason, checked_at)

    def _restricted(reason: str) -> PicoPlacaResult:
        return PicoPlacaResult(plate, city, cfg["name"], True, reason, checked_at)

    # festivos
    if is_holiday(now.date()) and not cfg["applies_on_holidays"]:
        return _no_restriction("Día festivo — sin restricción")

    # día no activo (sábado/domingo)
    if day_name not in cfg["active_days"]:
        return _no_restriction(f"{day_name.capitalize()} no tiene restricción")

    # verificar horario pico
    current_time = now.time()
    in_peak = False
    for start_str, end_str in cfg["peak_hours"]:
        from datetime import time
        start = time.fromisoformat(start_str)
        end = time.fromisoformat(end_str)
        if start <= current_time <= end:
            in_peak = True
            break

    if not in_peak:
        return _no_restriction("Fuera de horario pico")

    # último dígito de la placa
    digits = [c for c in plate if c.isdigit()]
    if not digits:
        return _no_restriction("Placa sin dígitos — no aplica restricción")

    last_digit = int(digits[-1])
    restricted_digits: list[int] = cfg["restrictions"].get(day_name, [])

    if last_digit in restricted_digits:
        return _restricted(
            f"Dígito {last_digit} restringido los {day_name.capitalize()} en horario pico"
        )

    return _no_restriction(f"Dígito {last_digit} no restringido hoy")
