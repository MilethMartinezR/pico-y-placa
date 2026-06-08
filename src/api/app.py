import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import json
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Flask, render_template

from src.api.routes.health import health_bp
from src.api.routes.validate import validate_bp

RULES_PATH = Path(__file__).resolve().parents[2] / "src" / "rules" / "restrictions.json"
DAY_MAP = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
DAY_ES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MONTH_ES = ["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"]


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )

    app.register_blueprint(health_bp)
    app.register_blueprint(validate_bp)

    @app.get("/")
    def index():
        now = datetime.now(ZoneInfo("America/Bogota"))
        day_name = DAY_ES[now.weekday()]
        date_str = f"{day_name}, {now.day} de {MONTH_ES[now.month-1]} de {now.year}"
        return render_template("index.html", date_str=date_str)

    @app.get("/validador")
    def validador():
        return render_template("validador.html")

    @app.get("/normas")
    def normas():
        with open(RULES_PATH, encoding="utf-8") as f:
            rules = json.load(f)
        return render_template("normas.html", rules=rules)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
