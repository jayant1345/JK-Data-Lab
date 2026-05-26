'use strict';

// ── Sidebar toggle (mobile) ───────────────────────────────
(function () {
  const btn = document.getElementById('sidebar-toggle');
  const sidebar = document.getElementById('admin-sidebar');
  if (!btn || !sidebar) return;
  btn.addEventListener('click', () => sidebar.classList.toggle('open'));
})();

// ── Auto-dismiss flash messages ───────────────────────────
setTimeout(() => {
  document.querySelectorAll('.admin-flash').forEach(f => f.remove());
}, 5000);

// ── Confirm delete forms ──────────────────────────────────
document.querySelectorAll('form[data-confirm]').forEach(form => {
  form.addEventListener('submit', e => {
    if (!confirm(form.dataset.confirm || 'Are you sure?')) e.preventDefault();
  });
});
