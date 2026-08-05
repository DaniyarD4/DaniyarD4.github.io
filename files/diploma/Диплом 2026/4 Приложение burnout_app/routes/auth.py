"""Маршруты аутентификации: вход, регистрация, выход."""
import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from db import get_db
from auth_utils import hash_password, verify_password

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return _redirect_by_role()
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        with get_db() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE username=? AND is_active=1", (username,)
            ).fetchone()
        if user and verify_password(password, user["password_hash"]):
            session["user_id"] = user["id"]
            session["role"] = user["role"]
            session.permanent = bool(request.form.get("remember"))
            logger.info(f"Вход: {username} ({user['role']})")
            return _redirect_by_role()
        flash("Неверное имя пользователя или пароль.", "error")
    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return _redirect_by_role()
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        full_name = request.form.get("full_name", "").strip()
        department = request.form.get("department", "").strip()
        role = request.form.get("role", "tutor")
        if role not in ("tutor", "hr"):
            role = "tutor"
        errors = []
        if not username or len(username) < 3:
            errors.append("Имя пользователя должно содержать не менее 3 символов.")
        if not email or "@" not in email:
            errors.append("Введите корректный email.")
        if not password or len(password) < 6:
            errors.append("Пароль должен содержать не менее 6 символов.")
        if not errors:
            with get_db() as conn:
                exists = conn.execute(
                    "SELECT id FROM users WHERE username=? OR email=?", (username, email)
                ).fetchone()
                if exists:
                    errors.append("Пользователь с таким именем или email уже существует.")
                else:
                    conn.execute(
                        "INSERT INTO users (username, email, password_hash, role, full_name, department) VALUES (?,?,?,?,?,?)",
                        (username, email, hash_password(password), role, full_name or username, department)
                    )
                    flash("Регистрация прошла успешно! Войдите в систему.", "success")
                    return redirect(url_for("auth.login"))
        for e in errors:
            flash(e, "error")
    return render_template("auth/register.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Вы вышли из системы.", "info")
    return redirect(url_for("auth.login"))


def _redirect_by_role():
    role = session.get("role")
    if role == "hr":
        return redirect(url_for("hr.dashboard"))
    return redirect(url_for("tutor.dashboard"))
