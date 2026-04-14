/**
 * quiz.js — Interactive MCQ for Islamic Finance Course
 *
 * Reads the Answer Key table in each .quiz-section, then makes each
 * A/B/C/D option paragraph clickable:
 *   - Correct answer  → turns green with a ✓ prefix
 *   - Wrong answer    → turns red  with a ✗ prefix, and reveals the correct one in green
 *
 * Once a question is answered the options lock (no re-clicking).
 */

(function () {
  'use strict';

  function initQuiz(section) {
    // ── 1. Extract correct answers from the Answer Key table ──────────────
    const table = section.querySelector('table');
    if (!table) return;

    const answers = {};   // { "1": "C", "2": "A", ... }
    table.querySelectorAll('tbody tr').forEach(function (row) {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 2) {
        const qNum   = cells[0].textContent.trim();
        const letter = cells[1].textContent.trim().toUpperCase().charAt(0);
        if (qNum && /^\d+$/.test(qNum) && /^[A-D]$/.test(letter)) {
          answers[qNum] = letter;
        }
      }
    });

    if (Object.keys(answers).length === 0) return;

    // ── 2. Walk child <p> elements to identify questions and options ───────
    let currentQ = 0;

    Array.from(section.children).forEach(function (el) {
      if (el.tagName !== 'P') return;

      const text   = el.textContent.trim();
      const strong = el.querySelector('strong');

      // Question paragraph: has <strong> whose text starts with "N."
      if (strong && /^\d+\./.test(strong.textContent.trim())) {
        const m = strong.textContent.trim().match(/^(\d+)\./);
        if (m) currentQ = m[1];
        return;
      }

      // Option paragraph: starts with A) B) C) D)
      const optMatch = text.match(/^([A-D])\)/);
      if (optMatch && currentQ && answers[currentQ]) {
        const letter = optMatch[1];
        const qKey   = currentQ;

        el.classList.add('quiz-option');
        el.dataset.letter   = letter;
        el.dataset.question = qKey;

        el.addEventListener('click', function () {
          // Lock once this question is answered
          if (el.classList.contains('answered')) return;

          const correct = answers[qKey];

          // Mark every option for this question as locked
          section.querySelectorAll('.quiz-option[data-question="' + qKey + '"]')
            .forEach(function (opt) { opt.classList.add('answered'); });

          if (letter === correct) {
            el.classList.add('quiz-correct');
          } else {
            el.classList.add('quiz-incorrect');
            // Reveal the correct option in green
            section.querySelectorAll(
              '.quiz-option[data-question="' + qKey + '"][data-letter="' + correct + '"]'
            ).forEach(function (opt) { opt.classList.add('quiz-correct'); });
          }
        });
      }
    });
  }

  // Run after MkDocs Material's instant navigation re-renders the page
  function run() {
    document.querySelectorAll('.quiz-section').forEach(initQuiz);
  }

  // Standard page load
  document.addEventListener('DOMContentLoaded', run);

  // MkDocs Material instant navigation (page.js fires this after each navigation)
  document.addEventListener('DOMContentSwitch', run);
})();
