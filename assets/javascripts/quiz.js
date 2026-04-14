/**
 * quiz.js — Interactive MCQ for Islamic Finance Course
 *
 * Reads the Answer Key table in each .quiz-section, then makes each
 * A/B/C/D option paragraph clickable:
 *   - Correct answer  → turns green
 *   - Wrong answer    → turns red, and the correct option is revealed in green
 *
 * Once a question is answered the options lock (no re-clicking).
 */

(function () {
  'use strict';

  function initQuiz(section) {
    // Prevent double-init (instant navigation may call run() more than once)
    if (section.dataset.quizReady) return;
    section.dataset.quizReady = '1';

    // ── 1. Extract correct answers from the Answer Key table ────────────
    const table = section.querySelector('table');
    if (!table) return;

    const answers = {};   // { "1": "C", "2": "A", … }
    table.querySelectorAll('tbody tr').forEach(function (row) {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 2) {
        const qNum   = cells[0].textContent.trim();
        const letter = cells[1].textContent.trim().replace(/\*/g, '').toUpperCase().charAt(0);
        if (qNum && /^\d+$/.test(qNum) && /^[A-D]$/.test(letter)) {
          answers[qNum] = letter;
        }
      }
    });

    if (Object.keys(answers).length === 0) return;

    // ── 2. Walk ALL <p> descendants, identify questions then options ─────
    let currentQ = '0';

    section.querySelectorAll('p').forEach(function (el) {
      const text   = el.textContent.trim();
      const strong = el.querySelector('strong');

      // Question paragraph: the only <strong> child starts with "N."
      if (strong && /^\d+\./.test(strong.textContent.trim())) {
        const m = strong.textContent.trim().match(/^(\d+)\./);
        if (m) currentQ = m[1];
        return;
      }

      // Option paragraph: text starts with A) B) C) D)
      const optMatch = text.match(/^([A-D])\)/);
      if (!optMatch || !answers[currentQ]) return;

      const letter = optMatch[1];
      const qKey   = currentQ;

      el.classList.add('quiz-option');
      el.dataset.letter   = letter;
      el.dataset.question = qKey;

      el.addEventListener('click', function () {
        if (el.classList.contains('answered')) return;

        const correct = answers[qKey];

        // Lock every option for this question
        section.querySelectorAll('.quiz-option[data-question="' + qKey + '"]')
          .forEach(function (opt) { opt.classList.add('answered'); });

        if (letter === correct) {
          el.classList.add('quiz-correct');
        } else {
          el.classList.add('quiz-incorrect');
          // Reveal correct option in green
          section.querySelectorAll(
            '.quiz-option[data-question="' + qKey + '"][data-letter="' + correct + '"]'
          ).forEach(function (opt) { opt.classList.add('quiz-correct'); });
        }
      });
    });
  }

  function run() {
    document.querySelectorAll('.quiz-section').forEach(initQuiz);
  }

  // Script is at bottom of <body> — DOM is already ready, so call immediately.
  // Also listen for DOMContentLoaded in case this somehow executes early.
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }

  // MkDocs Material instant navigation re-renders content without a full reload.
  // Re-run whenever new nodes containing .quiz-section are inserted into the DOM.
  var observer = new MutationObserver(function (mutations) {
    var needsRun = false;
    mutations.forEach(function (m) {
      m.addedNodes.forEach(function (node) {
        if (node.nodeType === 1) {  // Element node
          if (node.classList.contains('quiz-section') || node.querySelector('.quiz-section')) {
            needsRun = true;
          }
        }
      });
    });
    if (needsRun) run();
  });

  observer.observe(document.body, { childList: true, subtree: true });

})();
