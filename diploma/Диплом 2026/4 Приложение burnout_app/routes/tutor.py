"""Маршруты тьютора: дашборд, опросник, результаты, история."""
import json
import logging
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from db import get_db
from auth_utils import tutor_required, get_current_user
from engine.inference import InferenceEngine
from engine.questions import ALL_QUESTIONS, MBI_ANSWERS, CBI_ANSWERS

logger = logging.getLogger(__name__)
tutor_bp = Blueprint("tutor", __name__, url_prefix="/tutor")

_engine = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = InferenceEngine()
    return _engine


@tutor_bp.route("/dashboard")
@tutor_required
def dashboard():
    user = get_current_user()
    with get_db() as conn:
        recent = conn.execute(
            "SELECT * FROM results WHERE user_id=? ORDER BY created_at DESC LIMIT 5",
            (user.id,)
        ).fetchall()
        all_results = conn.execute(
            "SELECT * FROM results WHERE user_id=? ORDER BY created_at ASC",
            (user.id,)
        ).fetchall()
    dynamics = _build_dynamics(all_results)
    return render_template("tutor/dashboard.html", recent=recent, dynamics=dynamics)


@tutor_bp.route("/survey", methods=["GET"])
@tutor_required
def survey():
    user = get_current_user()
    with get_db() as conn:
        conn.execute(
            "INSERT INTO tests (user_id) VALUES (?)", (user.id,)
        )
        test_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    return render_template(
        "tutor/survey.html",
        test_id=test_id,
        questions=ALL_QUESTIONS,
        mbi_answers=MBI_ANSWERS,
        cbi_answers=CBI_ANSWERS,
    )


@tutor_bp.route("/survey/submit", methods=["POST"])
@tutor_required
def survey_submit():
    user = get_current_user()
    test_id = request.form.get("test_id")

    with get_db() as conn:
        test = conn.execute(
            "SELECT * FROM tests WHERE id=? AND user_id=?", (test_id, user.id)
        ).fetchone()
        if not test:
            flash("Тест не найден.", "error")
            return redirect(url_for("tutor.survey"))

    # Собираем ответы
    answers = {}
    for q in ALL_QUESTIONS:
        val = request.form.get(q["id"])
        if val is None:
            flash("Пожалуйста, ответьте на все вопросы.", "error")
            return redirect(url_for("tutor.survey"))
        try:
            answers[q["id"]] = int(val)
        except (ValueError, TypeError):
            flash("Некорректные данные ответа.", "error")
            return redirect(url_for("tutor.survey"))

    # Обратные вопросы MBI
    if "mbi_9" in answers:
        answers["mbi_9"] = 6 - answers["mbi_9"]
    for rev_q in ["mbi_21", "mbi_22"]:
        if rev_q in answers:
            answers[rev_q] = 6 - answers[rev_q]

    # Сохраняем ответы
    with get_db() as conn:
        conn.execute(
            "UPDATE tests SET answers_json=?, completed_at=?, is_complete=1 WHERE id=?",
            (json.dumps(answers, ensure_ascii=False), datetime.utcnow().isoformat(), test_id)
        )

    # Запускаем inference engine
    engine = get_engine()
    ir = engine.run(answers)

    with get_db() as conn:
        conn.execute(
            """INSERT INTO results (test_id, user_id, burnout_level, scores_json, levels_json, fired_rules_json)
               VALUES (?,?,?,?,?,?)""",
            (test_id, user.id, ir["burnout_level"],
             json.dumps(ir["scores"], ensure_ascii=False),
             json.dumps(ir["levels"], ensure_ascii=False),
             json.dumps(ir["fired_rules"], ensure_ascii=False))
        )
        result_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        # Сохраняем рекомендации
        for i, expl in enumerate(ir["explanations"]):
            recs = ir["recommendations"]
            rec_text = recs[i] if i < len(recs) else (recs[-1] if recs else "")
            conn.execute(
                """INSERT INTO recommendations (result_id, user_id, rule_id, rule_name, recommendation_text, explanation_text, source_scale)
                   VALUES (?,?,?,?,?,?,?)""",
                (result_id, user.id, expl["rule"], expl["rule"], rec_text, expl["text"], expl["source"])
            )

    logger.info(f"Тест {test_id}: пользователь {user.username}, уровень={ir['burnout_level']}")
    return redirect(url_for("tutor.result", result_id=result_id))


@tutor_bp.route("/result/<int:result_id>")
@tutor_required
def result(result_id):
    user = get_current_user()
    with get_db() as conn:
        res = conn.execute(
            "SELECT * FROM results WHERE id=? AND user_id=?", (result_id, user.id)
        ).fetchone()
        if not res:
            flash("Результат не найден.", "error")
            return redirect(url_for("tutor.dashboard"))
        recs = conn.execute(
            "SELECT * FROM recommendations WHERE result_id=?", (result_id,)
        ).fetchall()
    scores = json.loads(res["scores_json"])
    levels = json.loads(res["levels_json"])
    return render_template(
        "tutor/result.html",
        result=res,
        scores=scores,
        levels=levels,
        recommendations=recs,
        scale_labels=get_engine().get_scale_descriptions(),
    )


@tutor_bp.route("/history")
@tutor_required
def history():
    user = get_current_user()
    with get_db() as conn:
        results = conn.execute(
            "SELECT * FROM results WHERE user_id=? ORDER BY created_at DESC",
            (user.id,)
        ).fetchall()
    return render_template("tutor/history.html", results=results)


def _build_dynamics(results):
    labels, levels_data = [], []
    data = {"EE": [], "DP": [], "PA": [], "PB": [], "WB": [], "CB": []}
    for r in results:
        labels.append(r["created_at"][:10])
        scores = json.loads(r["scores_json"])
        for k in data:
            data[k].append(scores.get(k, 0))
        levels_data.append(r["burnout_level"])
    return {"labels": labels, "scores": data, "levels": levels_data}
