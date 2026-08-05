"""Маршруты HR/куратора: список сотрудников, аналитика, статистика."""
import json
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request
from db import get_db
from auth_utils import hr_required, get_current_user

logger = logging.getLogger(__name__)
hr_bp = Blueprint("hr", __name__, url_prefix="/hr")


@hr_bp.route("/dashboard")
@hr_required
def dashboard():
    with get_db() as conn:
        total_tutors = conn.execute(
            "SELECT COUNT(*) FROM users WHERE role='tutor' AND is_active=1"
        ).fetchone()[0]
        total_tests = conn.execute("SELECT COUNT(*) FROM results").fetchone()[0]
        latest_results = _get_latest_results(conn)
    level_dist = {"low": 0, "medium": 0, "high": 0}
    for r in latest_results:
        level_dist[r["burnout_level"]] = level_dist.get(r["burnout_level"], 0) + 1
    high_risk_raw = [r for r in latest_results if r["burnout_level"] == "high"]
    # Обогащаем данными о пользователях
    high_risk = []
    with get_db() as conn:
        for r in high_risk_raw:
            user_row = conn.execute("SELECT * FROM users WHERE id=?", (r["user_id"],)).fetchone()
            high_risk.append({"result": r, "user": user_row})
    avg_scores = _calc_avg_scores(latest_results)
    monthly_data = _get_monthly_dynamics()
    dept_stats = _get_dept_stats(latest_results)
    return render_template(
        "hr/dashboard.html",
        total_tutors=total_tutors,
        total_tests=total_tests,
        level_dist=level_dist,
        high_risk=high_risk,
        avg_scores=avg_scores,
        monthly_data=monthly_data,
        dept_stats=dept_stats,
    )


@hr_bp.route("/employees")
@hr_required
def employees():
    filter_level = request.args.get("level", "all")
    filter_dept = request.args.get("dept", "all")
    with get_db() as conn:
        tutors = conn.execute(
            "SELECT * FROM users WHERE role='tutor' AND is_active=1 ORDER BY full_name"
        ).fetchall()
        departments = conn.execute(
            "SELECT DISTINCT department FROM users WHERE role='tutor' AND department IS NOT NULL AND department != ''"
        ).fetchall()
        departments = [d[0] for d in departments]

    employees_data = []
    for tutor in tutors:
        with get_db() as conn:
            last_result = conn.execute(
                "SELECT * FROM results WHERE user_id=? ORDER BY created_at DESC LIMIT 1",
                (tutor["id"],)
            ).fetchone()
            tests_count = conn.execute(
                "SELECT COUNT(*) FROM results WHERE user_id=?", (tutor["id"],)
            ).fetchone()[0]
        entry = {
            "user": tutor,
            "last_result": last_result,
            "burnout_level": last_result["burnout_level"] if last_result else None,
            "last_test_date": last_result["created_at"][:10] if last_result else None,
            "tests_count": tests_count,
        }
        if filter_level != "all" and entry["burnout_level"] != filter_level:
            continue
        if filter_dept != "all" and tutor["department"] != filter_dept:
            continue
        employees_data.append(entry)

    return render_template(
        "hr/employees.html",
        employees=employees_data,
        filter_level=filter_level,
        filter_dept=filter_dept,
        departments=departments,
    )


@hr_bp.route("/employee/<int:user_id>")
@hr_required
def employee_detail(user_id):
    with get_db() as conn:
        tutor = conn.execute(
            "SELECT * FROM users WHERE id=? AND role='tutor'", (user_id,)
        ).fetchone()
        if not tutor:
            flash("Сотрудник не найден.", "error")
            return redirect(url_for("hr.employees"))
        results = conn.execute(
            "SELECT * FROM results WHERE user_id=? ORDER BY created_at DESC",
            (user_id,)
        ).fetchall()
        last_recs = []
        if results:
            last_recs = conn.execute(
                "SELECT * FROM recommendations WHERE result_id=?",
                (results[0]["id"],)
            ).fetchall()
    dynamics = _build_dynamics_for_user(results)
    return render_template(
        "hr/employee_detail.html",
        tutor=tutor,
        results=results,
        dynamics=dynamics,
        last_recs=last_recs,
    )


@hr_bp.route("/analytics")
@hr_required
def analytics():
    with get_db() as conn:
        all_results = conn.execute(
            "SELECT * FROM results ORDER BY created_at ASC"
        ).fetchall()
        latest = _get_latest_results(conn)
    monthly = _get_monthly_dynamics()
    dept_stats = _get_dept_stats(latest)
    avg_subscales = _calc_avg_scores(all_results)
    risk_dynamics = _get_risk_dynamics()
    return render_template(
        "hr/analytics.html",
        monthly=monthly,
        dept_stats=dept_stats,
        avg_subscales=avg_subscales,
        risk_dynamics=risk_dynamics,
        total_tests=len(all_results),
    )


# ------------------------------------------------------------------
def _get_latest_results(conn):
    """Последний результат для каждого тьютора."""
    rows = conn.execute("""
        SELECT r.* FROM results r
        INNER JOIN (
            SELECT user_id, MAX(created_at) as max_date
            FROM results GROUP BY user_id
        ) sub ON r.user_id = sub.user_id AND r.created_at = sub.max_date
    """).fetchall()
    return rows


def _calc_avg_scores(results):
    sums = {"EE": 0, "DP": 0, "PA": 0, "PB": 0, "WB": 0, "CB": 0}
    count = len(results)
    if count == 0:
        return {k: 0 for k in sums}
    for r in results:
        scores = json.loads(r["scores_json"])
        for k in sums:
            sums[k] += scores.get(k, 0)
    return {k: round(v / count, 2) for k, v in sums.items()}


def _get_monthly_dynamics():
    now = datetime.utcnow()
    months = []
    for i in range(5, -1, -1):
        dt = now - timedelta(days=30 * i)
        months.append((dt.year, dt.month, dt.strftime("%b %Y")))
    labels = [m[2] for m in months]
    low_data, medium_data, high_data = [], [], []
    for year, month, _ in months:
        with get_db() as conn:
            results = conn.execute(
                "SELECT burnout_level FROM results WHERE strftime('%Y', created_at)=? AND strftime('%m', created_at)=?",
                (str(year), f"{month:02d}")
            ).fetchall()
        low_data.append(sum(1 for r in results if r["burnout_level"] == "low"))
        medium_data.append(sum(1 for r in results if r["burnout_level"] == "medium"))
        high_data.append(sum(1 for r in results if r["burnout_level"] == "high"))
    return {"labels": labels, "low": low_data, "medium": medium_data, "high": high_data}


def _get_dept_stats(latest_results):
    dept_map = defaultdict(lambda: {"low": 0, "medium": 0, "high": 0, "total": 0})
    for r in latest_results:
        with get_db() as conn:
            user = conn.execute("SELECT department FROM users WHERE id=?", (r["user_id"],)).fetchone()
        dept = (user["department"] if user and user["department"] else "Без подразделения")
        dept_map[dept][r["burnout_level"]] += 1
        dept_map[dept]["total"] += 1
    return dict(dept_map)


def _build_dynamics_for_user(results):
    labels, levels = [], []
    data = {"EE": [], "DP": [], "PA": [], "PB": [], "WB": [], "CB": []}
    for r in reversed(results):
        labels.append(r["created_at"][:10])
        scores = json.loads(r["scores_json"])
        for k in data:
            data[k].append(scores.get(k, 0))
        levels.append(r["burnout_level"])
    return {"labels": labels, "scores": data, "levels": levels}


def _get_risk_dynamics():
    now = datetime.utcnow()
    labels, risk_counts = [], []
    for i in range(5, -1, -1):
        dt = now - timedelta(days=30 * i)
        labels.append(dt.strftime("%b %Y"))
        with get_db() as conn:
            count = conn.execute(
                "SELECT COUNT(*) FROM results WHERE burnout_level='high' AND strftime('%Y', created_at)=? AND strftime('%m', created_at)=?",
                (str(dt.year), f"{dt.month:02d}")
            ).fetchone()[0]
        risk_counts.append(count)
    return {"labels": labels, "counts": risk_counts}
