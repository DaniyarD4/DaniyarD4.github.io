"""
auth_utils.py — Утилиты аутентификации через Flask session.
Заменяет Flask-Login без внешних зависимостей.
"""
import functools
from flask import session, redirect, url_for, flash, g
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db


class UserProxy:
    """Объект пользователя из сессии / БД (аналог current_user Flask-Login)."""
    def __init__(self, row=None):
        if row:
            self.id = row["id"]
            self.username = row["username"]
            self.email = row["email"]
            self.full_name = row["full_name"] or row["username"]
            self.role = row["role"]
            self.department = row["department"]
            self.is_active = bool(row["is_active"])
            self.is_authenticated = True
        else:
            self.id = None
            self.username = None
            self.full_name = None
            self.role = None
            self.department = None
            self.is_active = False
            self.is_authenticated = False


def get_current_user():
    """Возвращает текущего пользователя из сессии."""
    if "user_id" not in session:
        return UserProxy()
    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()
    return UserProxy(row) if row else UserProxy()


def login_required(f):
    """Декоратор: требует авторизации."""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Пожалуйста, войдите для доступа к этой странице.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def tutor_required(f):
    """Декоратор: только для тьюторов."""
    @functools.wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        user = get_current_user()
        if user.role != "tutor":
            flash("Доступ запрещён.", "error")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def hr_required(f):
    """Декоратор: только для HR."""
    @functools.wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        user = get_current_user()
        if user.role != "hr":
            flash("Доступ запрещён. Требуется роль HR.", "error")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return check_password_hash(hashed, password)
