"""
app.py — Точка входа Flask-приложения.
Экспертная система мониторинга эмоционального выгорания тьюторов.
Источники: MBI (Водопьянова–Старченкова, 2008), CBI (Шайгерова и др., 2025).
"""
import json
import logging
import os
from flask import Flask, redirect, url_for, g
from db import init_db, get_db
from auth_utils import get_current_user, hash_password

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "burnout-expert-system-vkr-2025-secret")
    app.config["KNOWLEDGE_BASE_PATH"] = os.path.join(
        os.path.dirname(__file__), "knowledge_base", "rules.json"
    )

    # Jinja2 фильтры
    app.jinja_env.filters["fromjson"] = json.loads

    def format_date(value, fmt="%d.%m.%Y"):
        """Форматирует дату из строки ISO или datetime объекта."""
        if not value:
            return ""
        if hasattr(value, "strftime"):
            return value.strftime(fmt)
        try:
            # SQLite возвращает строки вида '2025-01-15 10:30:00'
            from datetime import datetime
            dt = datetime.fromisoformat(str(value)[:19])
            return dt.strftime(fmt)
        except Exception:
            return str(value)[:10]

    app.jinja_env.filters["dateformat"] = format_date

    # Инжект current_user во все шаблоны
    @app.context_processor
    def inject_user():
        return {"current_user": get_current_user()}

    # Регистрация Blueprint'ов
    from routes.auth import auth_bp
    from routes.tutor import tutor_bp
    from routes.hr import hr_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(tutor_bp)
    app.register_blueprint(hr_bp)

    @app.route("/")
    def index():
        return redirect(url_for("auth.login"))

    # Инициализация БД
    init_db()
    _seed_demo_data()

    return app


def _seed_demo_data():
    """Создаёт демонстрационных пользователей, если БД пуста."""
    with get_db() as conn:
        count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if count > 0:
            return
        logger.info("Создание демонстрационных пользователей...")
        demo_users = [
            ("tutor1", "tutor1@example.com", "Анна Петрова", "Отдел дистанционного обучения", "tutor", "tutor123"),
            ("tutor2", "tutor2@example.com", "Иван Сидоров", "Кафедра педагогики", "tutor", "tutor123"),
            ("tutor3", "tutor3@example.com", "Мария Козлова", "Отдел дистанционного обучения", "tutor", "tutor123"),
            ("hr_admin", "hr@example.com", "Елена Новикова", "HR-отдел", "hr", "hr123456"),
        ]
        for username, email, full_name, dept, role, password in demo_users:
            conn.execute(
                "INSERT INTO users (username, email, full_name, department, role, password_hash) VALUES (?,?,?,?,?,?)",
                (username, email, full_name, dept, role, hash_password(password))
            )
        logger.info(f"Создано {len(demo_users)} демо-пользователей.")


if __name__ == "__main__":
    app = create_app()
    logger.info("Запуск сервера на http://127.0.0.1:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
