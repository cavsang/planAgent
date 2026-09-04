/*
 * problem.html에서 아래처럼 설정을 먼저 심어준 뒤 이 파일을 로드해야 합니다:
 *
 * <script>
 *   window.QUIZ_CONFIG = {
 *     pid: "{{ pid }}",
 *     agentEndpoint: "https://your-agent-server.example.com/api/grade"
 *   };
 * </script>
 * <script src="/static/js/problem.js" defer></script>
 */

(function () {
  const CONFIG = window.QUIZ_CONFIG || {};
  const AGENT_ENDPOINT = CONFIG.agentEndpoint || "https://your-agent-server.example.com/api/grade";
  const PID = CONFIG.pid || "";

  function initHintToggles() {
    document.querySelectorAll(".hint-toggle").forEach((btn) => {
      btn.addEventListener("click", () => {
        const target = document.getElementById(btn.dataset.target);
        if (!target) return;
        const expanded = btn.getAttribute("aria-expanded") === "true";
        target.hidden = expanded;
        btn.setAttribute("aria-expanded", String(!expanded));
        btn.textContent = expanded ? "💡 힌트 보기" : "💡 힌트 닫기";
      });
    });
  }

  function collectAnswers(form) {
    const problemEls = form.querySelectorAll(".problem[data-pid]");
    return Array.from(problemEls).map((el) => {
      const pid = el.dataset.pid;
      const checked = el.querySelector(`input[type="radio"][name="${pid}"]:checked`);
      let answer;
      if (checked) {
        answer = checked.value;
      } else {
        const field = el.querySelector(`[name="${pid}"]`);
        answer = field ? field.value.trim() : "";
      }
      return { id: pid, answer };
    });
  }

  function findUnanswered(answers) {
    return answers.filter((a) => a.answer === "").map((a) => a.id);
  }

  function initSubmit() {
    const form = document.getElementById("quiz-form");
    const submitBtn = document.getElementById("submit-btn");
    const statusEl = document.getElementById("status");
    const resultPanel = document.getElementById("result-panel");
    if (!form || !submitBtn) return;

    submitBtn.addEventListener("click", async () => {
      const answers = collectAnswers(form);
      const unanswered = findUnanswered(answers);

      if (unanswered.length > 0) {
        statusEl.textContent = `아직 답하지 않은 문제가 있습니다: ${unanswered.join(", ")}`;
        statusEl.className = "error";
        return;
      }

      submitBtn.disabled = true;
      statusEl.textContent = "채점 중...";
      statusEl.className = "";
      if (resultPanel) resultPanel.style.display = "none";

      try {
        const response = await fetch(AGENT_ENDPOINT, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            pid: PID,
            submitted_at: new Date().toISOString(),
            answers
          })
        });

        if (!response.ok) throw new Error(`서버 응답 오류 (${response.status})`);

        const result = await response.json();
        statusEl.textContent = "제출 완료";
        statusEl.className = "ok";
        if (resultPanel) {
          resultPanel.style.display = "block";
          resultPanel.textContent = JSON.stringify(result, null, 2);
        }
      } catch (err) {
        statusEl.textContent = `제출 실패: ${err.message}`;
        statusEl.className = "error";
      } finally {
        submitBtn.disabled = false;
      }
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    initHintToggles();
    initSubmit();
  });
})();
