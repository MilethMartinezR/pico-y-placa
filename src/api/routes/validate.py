import io

import cv2
import numpy as np
from flask import Blueprint, jsonify, request

from src.pipeline import run

validate_bp = Blueprint("validate", __name__)

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


@validate_bp.post("/validate")
def validate():
    city = request.form.get("city", "bogota").lower().strip()

    # modo texto manual
    plate_text = request.form.get("plate_text", "").strip().upper()
    if plate_text and "image" not in request.files:
        import re
        from src.rules.pico_placa_engine import check
        if not re.match(r"[A-Z]{2,3}\d{3}|[A-Z]{2}\d{2}[A-Z]", plate_text):
            return jsonify({"error": "Formato de placa inválido. Ejemplo: ABC123"}), 422
        try:
            r = check(plate_text, city)
        except ValueError as e:
            return jsonify({"error": str(e)}), 422
        return jsonify({
            "plate": r.plate,
            "city": r.city_name,
            "restricted": r.restricted,
            "reason": r.reason,
            "checked_at": r.checked_at,
        })

    # modo imagen
    if "image" not in request.files:
        return jsonify({"error": "Sube una imagen o ingresa la placa manualmente"}), 400

    file = request.files["image"]

    if file.content_type not in ALLOWED_TYPES:
        return jsonify({"error": "Formato no soportado. Use JPEG, PNG o WebP"}), 415

    raw = file.read(MAX_SIZE_BYTES + 1)
    if len(raw) > MAX_SIZE_BYTES:
        return jsonify({"error": "Imagen demasiado grande (máx 5 MB)"}), 413

    arr = np.frombuffer(raw, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        return jsonify({"error": "No se pudo decodificar la imagen"}), 400

    result = run(img, city)

    if not result.success:
        return jsonify({"error": result.error}), 422

    r = result.restriction
    return jsonify({
        "plate": result.plate,
        "city": r.city_name,
        "restricted": r.restricted,
        "reason": r.reason,
        "checked_at": r.checked_at,
    })
