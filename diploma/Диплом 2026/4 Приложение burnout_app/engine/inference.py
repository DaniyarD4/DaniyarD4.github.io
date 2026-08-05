"""
Inference Engine — Продукционная экспертная система выявления выгорания.
Реализует механизм прямого вывода (forward chaining) на основе правил IF-THEN.
Источники: MBI (Водопьянова–Старченкова, 2008) и CBI (Шайгерова и др., 2025).
"""
import json
import os
import logging

logger = logging.getLogger(__name__)

KB_PATH = os.path.join(os.path.dirname(__file__), "..", "knowledge_base", "rules.json")


class InferenceEngine:
    """
    Экспертная система с продукционной моделью IF-THEN и механизмом прямого вывода.

    Алгоритм работы:
    1. Вычислить оценки по субшкалам MBI и CBI из ответов пользователя.
    2. Классифицировать каждую субшкалу (low / medium / high) по пороговым значениям.
    3. Перебрать все правила в базе знаний.
    4. Для каждого правила проверить: все ли условия (conditions) выполнены.
    5. Сработавшие (fired) правила собрать в список.
    6. Определить итоговый уровень выгорания по максимальному приоритету сработавших правил.
    7. Вернуть результат с объяснением и рекомендациями.
    """

    BURNOUT_PRIORITY = {"low": 0, "medium": 1, "high": 2}

    def __init__(self):
        self.rules = []
        self.thresholds = {}
        self._load_knowledge_base()

    def _load_knowledge_base(self):
        try:
            with open(KB_PATH, "r", encoding="utf-8") as f:
                kb = json.load(f)
            self.rules = kb["rules"]
            self.thresholds = kb["thresholds"]
            logger.info(f"База знаний загружена: {len(self.rules)} правил")
        except Exception as e:
            logger.error(f"Ошибка загрузки базы знаний: {e}")
            raise

    # ------------------------------------------------------------------
    # Шаг 1: Подсчёт баллов по субшкалам
    # ------------------------------------------------------------------

    def compute_subscale_scores(self, answers: dict) -> dict:
        """
        Вычисляет баллы по 6 субшкалам из словаря ответов.

        answers: {question_id: score}  (score 0–6 для MBI, 0/25/50/75/100 для CBI)
        Возвращает: {EE, DP, PA, PB, WB, CB}
        """
        # --- MBI субшкалы (ответы 0-6) ---
        # Эмоциональное истощение: вопросы mbi_1–mbi_9
        ee_items = [f"mbi_{i}" for i in range(1, 10)]
        # Деперсонализация: вопросы mbi_10–mbi_14
        dp_items = [f"mbi_{i}" for i in range(10, 15)]
        # Редукция достижений: вопросы mbi_15–mbi_22 (mbi_15–mbi_22 прямые + обратный)
        pa_items = [f"mbi_{i}" for i in range(15, 23)]
        # mbi_15–mbi_22 — прямой порядок (для редукции высокие баллы = НИЗКОЕ выгорание)
        # Поэтому для PA используем обратный подсчёт согласно ключу MBI

        ee_score = sum(answers.get(q, 0) for q in ee_items)
        dp_score = sum(answers.get(q, 0) for q in dp_items)
        # PA: максимум 6*8=48; высокий балл = низкое выгорание (обратная шкала)
        pa_score = sum(answers.get(q, 0) for q in pa_items)

        # --- CBI субшкалы (ответы 0, 25, 50, 75, 100) ---
        # Личностное выгорание: вопросы cbi_1–cbi_6
        pb_items = [f"cbi_{i}" for i in range(1, 7)]
        # Рабочее выгорание: вопросы cbi_7–cbi_13 (cbi_10 — обратный)
        wb_items = [f"cbi_{i}" for i in range(7, 14)]
        # Выгорание от взаимодействия: вопросы cbi_14–cbi_19
        cb_items = [f"cbi_{i}" for i in range(14, 20)]

        pb_vals = [answers.get(q, 0) for q in pb_items]
        pb_score = sum(pb_vals) / len(pb_vals) if pb_vals else 0

        wb_raw = []
        for item in wb_items:
            val = answers.get(item, 0)
            if item == "cbi_10":
                # Обратный вопрос: 0→100, 25→75, 50→50, 75→25, 100→0
                val = 100 - val
            wb_raw.append(val)
        wb_score = sum(wb_raw) / len(wb_raw) if wb_raw else 0

        cb_vals = [answers.get(q, 0) for q in cb_items]
        cb_score = sum(cb_vals) / len(cb_vals) if cb_vals else 0

        return {
            "EE": round(ee_score, 2),
            "DP": round(dp_score, 2),
            "PA": round(pa_score, 2),
            "PB": round(pb_score, 2),
            "WB": round(wb_score, 2),
            "CB": round(cb_score, 2),
        }

    # ------------------------------------------------------------------
    # Шаг 2: Классификация субшкал
    # ------------------------------------------------------------------

    def classify_subscales(self, scores: dict) -> dict:
        """
        Классифицирует каждую субшкалу как low / medium / high
        по пороговым значениям из базы знаний.
        """
        levels = {}

        # MBI пороги
        mbi_t = self.thresholds["MBI"]
        for scale in ["EE", "DP"]:
            v = scores[scale]
            t = mbi_t[scale]
            if t["low"][0] <= v <= t["low"][1]:
                levels[scale] = "low"
            elif t["medium"][0] <= v <= t["medium"][1]:
                levels[scale] = "medium"
            else:
                levels[scale] = "high"

        # PA — обратная шкала (высокий балл = низкое выгорание)
        pa_v = scores["PA"]
        pa_t = mbi_t["PA"]
        if pa_t["low"][0] <= pa_v <= pa_t["low"][1]:
            levels["PA"] = "low"  # low PA score = HIGH burnout on reduced achievement
        elif pa_t["medium"][0] <= pa_v <= pa_t["medium"][1]:
            levels["PA"] = "medium"
        else:
            levels["PA"] = "high"  # high PA score means GOOD achievement = LOW burnout

        # CBI пороги
        cbi_t = self.thresholds["CBI"]
        for scale in ["PB", "WB", "CB"]:
            v = scores[scale]
            t = cbi_t[scale]
            if t["low"][0] <= v <= t["low"][1]:
                levels[scale] = "low"
            elif t["medium"][0] <= v <= t["medium"][1]:
                levels[scale] = "medium"
            else:
                levels[scale] = "high"

        return levels

    # ------------------------------------------------------------------
    # Шаг 3: Применение правил (forward chaining)
    # ------------------------------------------------------------------

    def _rule_matches(self, rule: dict, levels: dict) -> bool:
        """Проверяет, выполнены ли все условия правила (AND-логика)."""
        conditions = rule.get("conditions", {})
        for scale, required_level in conditions.items():
            if levels.get(scale) != required_level:
                return False
        return True

    def apply_rules(self, levels: dict) -> list:
        """Возвращает список всех сработавших правил."""
        fired = []
        for rule in self.rules:
            if self._rule_matches(rule, levels):
                fired.append(rule)
                logger.debug(f"Правило сработало: {rule['id']} — {rule['name']}")
        return fired

    # ------------------------------------------------------------------
    # Шаг 4: Определение итогового уровня выгорания
    # ------------------------------------------------------------------

    def determine_burnout_level(self, fired_rules: list) -> str:
        """Определяет финальный уровень выгорания по сработавшим правилам."""
        if not fired_rules:
            return "low"
        max_priority = max(
            self.BURNOUT_PRIORITY.get(r["burnout_level"], 0) for r in fired_rules
        )
        for level, priority in self.BURNOUT_PRIORITY.items():
            if priority == max_priority:
                return level
        return "low"

    # ------------------------------------------------------------------
    # Главная точка входа
    # ------------------------------------------------------------------

    def run(self, answers: dict) -> dict:
        """
        Полный цикл вывода: от ответов к итоговому результату.
        Возвращает dict со всеми данными для сохранения и отображения.
        """
        # 1. Подсчёт баллов
        scores = self.compute_subscale_scores(answers)

        # 2. Классификация
        levels = self.classify_subscales(scores)

        # 3. Применение правил
        fired_rules = self.apply_rules(levels)

        # 4. Итоговый уровень
        burnout_level = self.determine_burnout_level(fired_rules)

        # 5. Подготовка результата
        recommendations = [r["recommendation"] for r in fired_rules]
        explanations = [
            {"rule": r["name"], "text": r["explanation"], "source": r["source_scale"]}
            for r in fired_rules
        ]

        # Убираем дубликаты рекомендаций
        seen = set()
        unique_recs = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recs.append(rec)

        return {
            "scores": scores,
            "levels": levels,
            "burnout_level": burnout_level,
            "fired_rules": [r["id"] for r in fired_rules],
            "fired_rules_count": len(fired_rules),
            "recommendations": unique_recs,
            "explanations": explanations,
        }

    def get_scale_descriptions(self) -> dict:
        """Возвращает описания субшкал для отображения в интерфейсе."""
        return {
            "EE": "Эмоциональное истощение (MBI)",
            "DP": "Деперсонализация (MBI)",
            "PA": "Редукция достижений (MBI)",
            "PB": "Личностное выгорание (CBI)",
            "WB": "Рабочее выгорание (CBI)",
            "CB": "Выгорание от взаимодействия (CBI)",
        }
