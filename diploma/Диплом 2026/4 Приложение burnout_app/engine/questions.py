"""
Вопросы опросника на основе MBI (Водопьянова–Старченкова, 2008)
и CBI (Шайгерова и др., 2025) для тьюторов.
"""

# Варианты ответов MBI (0-6 баллов)
MBI_ANSWERS = [
    {"value": 0, "label": "Никогда"},
    {"value": 1, "label": "Очень редко"},
    {"value": 2, "label": "Редко"},
    {"value": 3, "label": "Иногда"},
    {"value": 4, "label": "Часто"},
    {"value": 5, "label": "Очень часто"},
    {"value": 6, "label": "Каждый день"},
]

# Варианты ответов CBI (по 5-балльной шкале → 0/25/50/75/100)
CBI_ANSWERS = [
    {"value": 100, "label": "Постоянно или в очень сильной степени"},
    {"value": 75,  "label": "Часто или в сильной степени"},
    {"value": 50,  "label": "Иногда или в некоторой степени"},
    {"value": 25,  "label": "Редко"},
    {"value": 0,   "label": "Никогда / очень редко или совсем незначительно"},
]

# Вопросы MBI — адаптированы для тьюторов на основе варианта опросника ПВ
# (Водопьянова, Старченкова, 2008, с. 153–158)
MBI_QUESTIONS = [
    # --- Эмоциональное истощение (EE) — вопросы mbi_1 – mbi_9 ---
    {
        "id": "mbi_1",
        "subscale": "EE",
        "subscale_name": "Эмоциональное истощение",
        "text": "К концу рабочей недели я чувствую себя эмоционально опустошённым(ой).",
        "scale": "MBI",
        "reverse": False,
    },
    {
        "id": "mbi_2",
        "subscale": "EE",
        "subscale_name": "Эмоциональное истощение",
        "text": "К концу рабочего дня я чувствую себя как выжатый лимон.",
        "scale": "MBI",
        "reverse": False,
    },
    {
        "id": "mbi_3",
        "subscale": "EE",
        "subscale_name": "Эмоциональное истощение",
        "text": "Я чувствую себя усталым(ой), когда встаю утром и должен(должна) идти на работу.",
        "scale": "MBI",
        "reverse": False,
    },
    {
        "id": "mbi_4",
        "subscale": "EE",
        "subscale_name": "Эмоциональное истощение",
        "text": "Работа с тьюторантами в течение всего дня — это большое напряжение для меня.",
        "scale": "MBI",
        "reverse": False,
    },
    {
        "id": "mbi_5",
        "subscale": "EE",
        "subscale_name": "Эмоциональное истощение",
        "text": "Я чувствую угнетённость и апатию.",
        "scale": "MBI",
        "reverse": False,
    },
    {
        "id": "mbi_6",
        "subscale": "EE",
        "subscale_name": "Эмоциональное истощение",
        "text": "Я чувствую равнодушие и потерю интереса ко многому, что радовало меня раньше.",
        "scale": "MBI",
        "reverse": False,
    },
    {
        "id": "mbi_7",
        "subscale": "EE",
        "subscale_name": "Эмоциональное истощение",
        "text": "Я чувствую себя на пределе возможностей.",
        "scale": "MBI",
        "reverse": False,
    },
    {
        "id": "mbi_8",
        "subscale": "EE",
        "subscale_name": "Эмоциональное истощение",
        "text": "Мне хочется уединиться и отдохнуть от всего и всех.",
        "scale": "MBI",
        "reverse": False,
    },
    {
        "id": "mbi_9",
        "subscale": "EE",
        "subscale_name": "Эмоциональное истощение",
        "text": "Я чувствую себя энергичным(ой) и эмоционально воодушевлённым(ой).",
        "scale": "MBI",
        "reverse": True,  # Обратный вопрос
    },
    # --- Деперсонализация (DP) — вопросы mbi_10 – mbi_14 ---
    {
        "id": "mbi_10",
        "subscale": "DP",
        "subscale_name": "Деперсонализация",
        "text": "В последнее время я стал(а) более черствым(ой) по отношению к тем, с кем работаю.",
        "scale": "MBI",
        "reverse": False,
    },
    {
        "id": "mbi_11",
        "subscale": "DP",
        "subscale_name": "Деперсонализация",
        "text": "Тьюторанты и коллеги, с которыми мне приходится работать, скорее утомляют, чем радуют меня.",
        "scale": "MBI",
        "reverse": False,
    },
    {
        "id": "mbi_12",
        "subscale": "DP",
        "subscale_name": "Деперсонализация",
        "text": "Я предпочитаю формальное общение с тьюторантами, без лишних эмоций, и стремлюсь свести его до минимума.",
        "scale": "MBI",
        "reverse": False,
    },
    {
        "id": "mbi_13",
        "subscale": "DP",
        "subscale_name": "Деперсонализация",
        "text": "Мне безразлично, что происходит с моими тьюторантами.",
        "scale": "MBI",
        "reverse": False,
    },
    {
        "id": "mbi_14",
        "subscale": "DP",
        "subscale_name": "Деперсонализация",
        "text": "Тьюторанты любят перекладывать на меня груз своих проблем и обязанностей.",
        "scale": "MBI",
        "reverse": False,
    },
    # --- Редукция персональных достижений (PA) — вопросы mbi_15 – mbi_22 ---
    {
        "id": "mbi_15",
        "subscale": "PA",
        "subscale_name": "Редукция достижений",
        "text": "Я легко могу создать атмосферу доброжелательности и сотрудничества при работе с тьюторантами.",
        "scale": "MBI",
        "reverse": False,  # Высокий балл = низкое выгорание
    },
    {
        "id": "mbi_16",
        "subscale": "PA",
        "subscale_name": "Редукция достижений",
        "text": "Я лёгко общаюсь с тьюторантами, независимо от их амбиций и эмоционального состояния.",
        "scale": "MBI",
        "reverse": False,
    },
    {
        "id": "mbi_17",
        "subscale": "PA",
        "subscale_name": "Редукция достижений",
        "text": "Я доволен(довольна) своими профессиональными достижениями как тьютора.",
        "scale": "MBI",
        "reverse": False,
    },
    {
        "id": "mbi_18",
        "subscale": "PA",
        "subscale_name": "Редукция достижений",
        "text": "У меня много планов на будущее в профессии, и я верю в их осуществление.",
        "scale": "MBI",
        "reverse": False,
    },
    {
        "id": "mbi_19",
        "subscale": "PA",
        "subscale_name": "Редукция достижений",
        "text": "Я оказываю позитивное влияние на развитие и продуктивность моих тьюторантов.",
        "scale": "MBI",
        "reverse": False,
    },
    {
        "id": "mbi_20",
        "subscale": "PA",
        "subscale_name": "Редукция достижений",
        "text": "Я умею находить правильное решение в сложных ситуациях при работе с тьюторантами.",
        "scale": "MBI",
        "reverse": False,
    },
    {
        "id": "mbi_21",
        "subscale": "PA",
        "subscale_name": "Редукция достижений",
        "text": "Результаты моей работы как тьютора не стоят тех усилий, которые я затрачиваю.",
        "scale": "MBI",
        "reverse": True,  # Обратный — низкий балл = хорошо для PA
    },
    {
        "id": "mbi_22",
        "subscale": "PA",
        "subscale_name": "Редукция достижений",
        "text": "У меня много жизненных разочарований.",
        "scale": "MBI",
        "reverse": True,
    },
    # --- CBI: Личностное выгорание (PB) — вопросы cbi_1–cbi_6 ---
    {
        "id": "cbi_1",
        "subscale": "PB",
        "subscale_name": "Личностное выгорание",
        "text": "Как часто Вы чувствуете усталость?",
        "scale": "CBI",
        "reverse": False,
    },
    {
        "id": "cbi_2",
        "subscale": "PB",
        "subscale_name": "Личностное выгорание",
        "text": "Как часто Вы «выжаты» физически?",
        "scale": "CBI",
        "reverse": False,
    },
    {
        "id": "cbi_3",
        "subscale": "PB",
        "subscale_name": "Личностное выгорание",
        "text": "Как часто Вы опустошены эмоционально?",
        "scale": "CBI",
        "reverse": False,
    },
    {
        "id": "cbi_4",
        "subscale": "PB",
        "subscale_name": "Личностное выгорание",
        "text": "Как часто у Вас возникает мысль: «Я больше не смогу этого вынести»?",
        "scale": "CBI",
        "reverse": False,
    },
    {
        "id": "cbi_5",
        "subscale": "PB",
        "subscale_name": "Личностное выгорание",
        "text": "Как часто Вы чувствуете себя измождённым(ой)?",
        "scale": "CBI",
        "reverse": False,
    },
    {
        "id": "cbi_6",
        "subscale": "PB",
        "subscale_name": "Личностное выгорание",
        "text": "Как часто Вы чувствуете слабость или что находитесь на грани заболевания?",
        "scale": "CBI",
        "reverse": False,
    },
    # --- CBI: Рабочее выгорание (WB) — вопросы cbi_7–cbi_13 ---
    {
        "id": "cbi_7",
        "subscale": "WB",
        "subscale_name": "Рабочее выгорание",
        "text": "Как часто Вы чувствуете себя измотанным(ой) в конце рабочего дня?",
        "scale": "CBI",
        "reverse": False,
    },
    {
        "id": "cbi_8",
        "subscale": "WB",
        "subscale_name": "Рабочее выгорание",
        "text": "Вы чувствуете опустошение по утрам при мысли о предстоящем рабочем дне?",
        "scale": "CBI",
        "reverse": False,
    },
    {
        "id": "cbi_9",
        "subscale": "WB",
        "subscale_name": "Рабочее выгорание",
        "text": "Вы чувствуете, что с каждым часом на работе утомление усиливается?",
        "scale": "CBI",
        "reverse": False,
    },
    {
        "id": "cbi_10",
        "subscale": "WB",
        "subscale_name": "Рабочее выгорание",
        "text": "Вы чувствуете, что у Вас хватает энергии для семьи и друзей в свободное время?",
        "scale": "CBI",
        "reverse": True,  # Обратный вопрос CBI
    },
    {
        "id": "cbi_11",
        "subscale": "WB",
        "subscale_name": "Рабочее выгорание",
        "text": "Ваша работа опустошает эмоционально?",
        "scale": "CBI",
        "reverse": False,
    },
    {
        "id": "cbi_12",
        "subscale": "WB",
        "subscale_name": "Рабочее выгорание",
        "text": "Ваша работа раздражает Вас?",
        "scale": "CBI",
        "reverse": False,
    },
    {
        "id": "cbi_13",
        "subscale": "WB",
        "subscale_name": "Рабочее выгорание",
        "text": "Вы чувствуете истощение из-за Вашей работы?",
        "scale": "CBI",
        "reverse": False,
    },
    # --- CBI: Выгорание от взаимодействия (CB) — вопросы cbi_14–cbi_19 ---
    {
        "id": "cbi_14",
        "subscale": "CB",
        "subscale_name": "Выгорание от взаимодействия",
        "text": "Вы считаете, что работать с Вашими тьюторантами сложно?",
        "scale": "CBI",
        "reverse": False,
    },
    {
        "id": "cbi_15",
        "subscale": "CB",
        "subscale_name": "Выгорание от взаимодействия",
        "text": "Работа с Вашими тьюторантами отнимает у Вас много энергии?",
        "scale": "CBI",
        "reverse": False,
    },
    {
        "id": "cbi_16",
        "subscale": "CB",
        "subscale_name": "Выгорание от взаимодействия",
        "text": "Вы считаете, что работа с тьюторантами приводит к раздражению?",
        "scale": "CBI",
        "reverse": False,
    },
    {
        "id": "cbi_17",
        "subscale": "CB",
        "subscale_name": "Выгорание от взаимодействия",
        "text": "Вы считаете, что Вы отдаёте больше, чем получаете, когда работаете с тьюторантами?",
        "scale": "CBI",
        "reverse": False,
    },
    {
        "id": "cbi_18",
        "subscale": "CB",
        "subscale_name": "Выгорание от взаимодействия",
        "text": "Задумываетесь ли Вы о том, как долго Вы ещё сможете продолжать работать с тьюторантами?",
        "scale": "CBI",
        "reverse": False,
    },
    {
        "id": "cbi_19",
        "subscale": "CB",
        "subscale_name": "Выгорание от взаимодействия",
        "text": "Вы устаёте от работы с тьюторантами?",
        "scale": "CBI",
        "reverse": False,
    },
]

ALL_QUESTIONS = MBI_QUESTIONS


def get_questions_by_subscale():
    """Группирует вопросы по субшкалам для пошагового прохождения."""
    groups = {}
    for q in ALL_QUESTIONS:
        key = q["subscale"]
        if key not in groups:
            groups[key] = {"subscale": key, "subscale_name": q["subscale_name"], "questions": []}
        groups[key]["questions"].append(q)
    return groups


def get_answers_for_scale(scale_name: str):
    """Возвращает варианты ответов для нужной шкалы."""
    if scale_name == "MBI":
        return MBI_ANSWERS
    return CBI_ANSWERS
