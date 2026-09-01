(function () {
  const root = document.querySelector('[data-problem-app]');
  if (!root) return;

  const pid = root.dataset.pid;
  const isPreview = root.dataset.preview === 'true';

  const textareas = Array.from(root.querySelectorAll('.answer-box'));
  const chips = Array.from(root.querySelectorAll('.rail-chip'));
  const countEl = root.querySelector('#answered-count');
  const statusText = root.querySelector('#status-text');
  const submitBtn = root.querySelector('#submit-btn');
  const total = textareas.length;

  function refresh() {
    let filled = 0;
    textareas.forEach((ta, i) => {
      const has = ta.value.trim().length > 0;
      if (has) filled++;
      if (chips[i]) chips[i].classList.toggle('filled', has);
    });
    if (countEl) countEl.textContent = filled;
    if (statusText) statusText.innerHTML = `<strong>${filled}</strong>/${total} 작성됨`;
  }
  textareas.forEach((ta) => ta.addEventListener('input', refresh));
  refresh();

  function finishSuccess(message) {
    textareas.forEach((ta) => (ta.disabled = true));
    submitBtn.textContent = '제출 완료 ✓';
    statusText.classList.add('done');
    statusText.innerHTML = message;
  }

  submitBtn.addEventListener('click', async () => {
    const answers = textareas.map((ta) => ta.value.trim());
    submitBtn.disabled = true;
    submitBtn.textContent = '제출 중...';

    // 미리보기 모드(서버 없이 로컬에서 여는 경우)는 네트워크 호출 없이 완료 상태만 보여줍니다.
    if (isPreview) {
      window.setTimeout(() => {
        finishSuccess('✓ 제출이 완료되었습니다 (미리보기이므로 실제 전송은 되지 않습니다)');
      }, 400);
      return;
    }

    try {
      const res = await fetch(`/problem/${pid}/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pid, answers }),
      });
      if (!res.ok) throw new Error('submit failed');
      finishSuccess('✓ 제출이 완료되었습니다');
    } catch (err) {
      submitBtn.disabled = false;
      submitBtn.textContent = '답안 제출하기';
      alert('제출 중 문제가 발생했습니다. 다시 시도해주세요.');
    }
  });
})();
