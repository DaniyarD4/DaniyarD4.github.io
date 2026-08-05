/**
 * main.js — Утилиты интерфейса экспертной системы мониторинга выгорания тьюторов.
 * Источники: MBI (Водопьянова–Старченкова, 2008), CBI (Шайгерова и др., 2025)
 */

// ===========================================================
// Прогресс-бар опросника
// ===========================================================
(function () {
  const form = document.getElementById("survey-form");
  if (!form) return;

  const totalQuestions = form.querySelectorAll("input[type=radio]").length > 0
    ? new Set([...form.querySelectorAll("input[type=radio]")].map(r => r.name)).size
    : 0;

  const progressBar = document.getElementById("survey-progress");
  const progressText = document.getElementById("survey-progress-text");

  function updateProgress() {
    const answered = new Set(
      [...form.querySelectorAll("input[type=radio]:checked")].map(r => r.name)
    ).size;
    const pct = totalQuestions > 0 ? Math.round((answered / totalQuestions) * 100) : 0;
    if (progressBar) {
      progressBar.style.width = pct + "%";
      progressBar.setAttribute("aria-valuenow", pct);
    }
    if (progressText) {
      progressText.textContent = `${answered} / ${totalQuestions} вопросов (${pct}%)`;
    }
  }

  form.addEventListener("change", updateProgress);
  updateProgress();

  // Валидация перед отправкой
  form.addEventListener("submit", function (e) {
    const names = new Set([...form.querySelectorAll("input[type=radio]")].map(r => r.name));
    const answered = new Set(
      [...form.querySelectorAll("input[type=radio]:checked")].map(r => r.name)
    );
    const missing = [...names].filter(n => !answered.has(n));
    if (missing.length > 0) {
      e.preventDefault();
      const first = form.querySelector(`input[name="${missing[0]}"]`);
      if (first) {
        first.closest(".question-card").scrollIntoView({ behavior: "smooth", block: "center" });
        first.closest(".question-card").classList.add("question-error");
        setTimeout(() => first.closest(".question-card").classList.remove("question-error"), 2000);
      }
      showAlert(`Пожалуйста, ответьте на все вопросы. Осталось: ${missing.length}`, "warning");
    }
  });
})();

// ===========================================================
// Flash-уведомления: авто-скрытие через 5 сек
// ===========================================================
(function () {
  const alerts = document.querySelectorAll(".flash-alert");
  alerts.forEach(function (alert) {
    setTimeout(function () {
      alert.style.transition = "opacity 0.5s";
      alert.style.opacity = "0";
      setTimeout(() => alert.remove(), 500);
    }, 5000);
  });
})();

// ===========================================================
// Утилита: показать уведомление
// ===========================================================
function showAlert(message, type = "info") {
  const container = document.getElementById("flash-container") || document.body;
  const div = document.createElement("div");
  div.className = `flash-alert alert alert-${type}`;
  div.textContent = message;
  container.prepend(div);
  setTimeout(() => {
    div.style.transition = "opacity 0.5s";
    div.style.opacity = "0";
    setTimeout(() => div.remove(), 500);
  }, 5000);
}

// ===========================================================
// Инициализация тултипов Bootstrap (если подключён)
// ===========================================================
document.addEventListener("DOMContentLoaded", function () {
  if (typeof bootstrap !== "undefined" && bootstrap.Tooltip) {
    const tooltipEls = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipEls.forEach(el => new bootstrap.Tooltip(el));
  }
});
