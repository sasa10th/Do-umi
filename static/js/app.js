// ── Sidebar Toggle ────────────────────────────────
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebarOverlay');
  const isOpen = sidebar.classList.toggle('open');
  if (overlay) overlay.classList.toggle('active', isOpen);
}

function closeSidebar() {
  document.getElementById('sidebar').classList.remove('open');
  const overlay = document.getElementById('sidebarOverlay');
  if (overlay) overlay.classList.remove('active');
}

// ── Search ────────────────────────────────────────
let searchTimeout;
const searchInput = document.getElementById('searchInput');
const searchResults = document.getElementById('searchResults');

if (searchInput) {
  searchInput.addEventListener('input', () => {
    clearTimeout(searchTimeout);
    const q = searchInput.value.trim();
    if (q.length < 1) {
      searchResults.style.display = 'none';
      return;
    }
    searchTimeout = setTimeout(() => doSearch(q), 300);
  });

  document.addEventListener('click', (e) => {
    if (!searchInput.contains(e.target)) {
      searchResults.style.display = 'none';
    }
  });
}

async function doSearch(q) {
  try {
    const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
    const data = await res.json();

    let html = '';
    if (data.penalties.length === 0 && data.documents.length === 0) {
      html = '<div class="search-item search-item-empty">검색 결과가 없습니다.</div>';
    } else {
      data.penalties.forEach(p => {
        html += `<div class="search-item" onclick="location.href='/penalties'">
          <strong>벌점</strong> ${p.reason} <span class="search-item-date">${p.date}</span>
        </div>`;
      });
      data.documents.forEach(d => {
        html += `<div class="search-item" onclick="location.href='/documents'">
          <strong>천자문</strong> ${d.doc_type} <span class="search-item-date">${d.due_date}</span>
        </div>`;
      });
    }
    searchResults.innerHTML = html;
    searchResults.style.display = 'block';
  } catch (e) {
    console.error('Search error:', e);
  }
}

// ── Notification badge ────────────────────────────
async function updateNotifBadge() {
  try {
    const res = await fetch('/api/notifications/unread-count');
    const data = await res.json();
    const badge = document.getElementById('notif-badge');
    const topCount = document.getElementById('topNotifCount');
    if (data.count > 0) {
      if (badge) { badge.style.display = 'inline'; badge.textContent = data.count; }
      if (topCount) topCount.textContent = data.count;
    }
  } catch (e) {}
}

// ── 스크롤 위치 보존 ──────────────────────────────
// 정렬 변경(링크 이동)이나 폼 제출(리다이렉트) 후 같은 페이지로 돌아왔을 때
// 브라우저가 스크롤을 맨 위로 리셋하는 것을 방지하기 위해, 이동 직전 위치를
// sessionStorage에 저장해두고 페이지 로드 시 복원한다.
function saveScrollPosition() {
  sessionStorage.setItem('scrollPos:' + location.pathname, String(window.scrollY));
}

function restoreScrollPosition() {
  const key = 'scrollPos:' + location.pathname;
  const saved = sessionStorage.getItem(key);
  if (saved === null) return;
  sessionStorage.removeItem(key);
  const y = parseInt(saved, 10);
  if (!Number.isNaN(y)) {
    requestAnimationFrame(() => requestAnimationFrame(() => window.scrollTo(0, y)));
  }
}

// ── Toast 알림 ────────────────────────────────────
const TOAST_ICONS = {
  success: 'bi-check-circle-fill',
  danger:  'bi-x-circle-fill',
  warning: 'bi-exclamation-triangle-fill',
  info:    'bi-info-circle-fill',
};

function dismissToast(el) {
  if (!el || el.classList.contains('hide')) return;
  el.classList.remove('show');
  el.classList.add('hide');
  setTimeout(() => el.remove(), 250);
}

function showToast(message, category = 'info', timeout = 5000) {
  const container = document.getElementById('toastContainer');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast toast-${category}`;
  toast.setAttribute('role', 'alert');
  toast.innerHTML = `
    <span class="toast-icon"><i class="bi ${TOAST_ICONS[category] || TOAST_ICONS.info}"></i></span>
    <span class="toast-msg"></span>
    <button class="toast-close" aria-label="닫기">×</button>
  `;
  toast.querySelector('.toast-msg').textContent = message;
  toast.querySelector('.toast-close').addEventListener('click', () => dismissToast(toast));
  container.appendChild(toast);

  requestAnimationFrame(() => requestAnimationFrame(() => toast.classList.add('show')));
  if (timeout > 0) setTimeout(() => dismissToast(toast), timeout);
  return toast;
}

function initToasts() {
  document.querySelectorAll('#toastContainer .toast').forEach(toast => {
    toast.querySelector('.toast-close')?.addEventListener('click', () => dismissToast(toast));
    requestAnimationFrame(() => requestAnimationFrame(() => toast.classList.add('show')));
    setTimeout(() => dismissToast(toast), 5000);
  });
}

// ── 공통 확인 모달 (네이티브 confirm() 대체) ──────────────
function confirmDialog(message, { title = '확인', okText = '확인', danger = false } = {}) {
  return new Promise((resolve) => {
    const modal = document.getElementById('confirmModal');
    if (!modal) { resolve(window.confirm(message)); return; }

    const titleEl = document.getElementById('confirmModalTitle');
    const msgEl = document.getElementById('confirmModalMessage');
    const okBtn = document.getElementById('confirmModalOk');
    const cancelBtn = document.getElementById('confirmModalCancel');
    const backdrop = modal.querySelector('.modal-backdrop');

    titleEl.textContent = title;
    msgEl.textContent = message;
    okBtn.textContent = okText;
    okBtn.classList.toggle('btn-danger', danger);
    okBtn.classList.toggle('btn-primary', !danger);
    modal.style.display = 'flex';

    const cleanup = (result) => {
      modal.style.display = 'none';
      okBtn.removeEventListener('click', onOk);
      cancelBtn.removeEventListener('click', onCancel);
      backdrop.removeEventListener('click', onCancel);
      resolve(result);
    };
    const onOk = () => cleanup(true);
    const onCancel = () => cleanup(false);
    okBtn.addEventListener('click', onOk);
    cancelBtn.addEventListener('click', onCancel);
    backdrop.addEventListener('click', onCancel);
  });
}

// data-confirm 속성이 있는 폼은 제출 전 커스텀 확인 모달을 띄움
document.addEventListener('submit', (e) => {
  const form = e.target;
  if (form instanceof HTMLFormElement && form.dataset.confirm && !form.dataset.confirmed) {
    e.preventDefault();
    confirmDialog(form.dataset.confirm, { danger: form.dataset.confirmDanger === 'true' }).then(ok => {
      if (ok) {
        form.dataset.confirmed = '1';
        form.requestSubmit ? form.requestSubmit() : form.submit();
      }
    });
  }
}, true);

// ── 다크 모드 ──────────────────────────────────────
function applyTheme(theme) {
  if (theme === 'dark') document.documentElement.setAttribute('data-theme', 'dark');
  else document.documentElement.removeAttribute('data-theme');
  const icon = document.querySelector('#themeToggle i');
  if (icon) icon.className = theme === 'dark' ? 'bi bi-sun' : 'bi bi-moon-stars';
  document.dispatchEvent(new CustomEvent('themechange', { detail: { theme } }));
}

function initThemeToggle() {
  const btn = document.getElementById('themeToggle');
  if (!btn) return;
  applyTheme(document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light');
  btn.addEventListener('click', () => {
    const next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    localStorage.setItem('theme', next);
    applyTheme(next);
  });
}

// ── 숫자 카운트업 애니메이션 ──────────────────────────
function animateCountUp(el, duration = 900) {
  const text = el.textContent.trim();
  const match = text.match(/^(-?[\d,]+)(.*)$/);
  if (!match) return;
  const target = parseInt(match[1].replace(/,/g, ''), 10);
  const suffix = match[2];
  if (Number.isNaN(target)) return;

  const start = performance.now();
  function tick(now) {
    const t = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - t, 3);
    const current = Math.round(target * eased);
    el.textContent = current.toLocaleString() + suffix;
    if (t < 1) requestAnimationFrame(tick);
    else el.textContent = target.toLocaleString() + suffix;
  }
  requestAnimationFrame(tick);
}

function initCountUps() {
  document.querySelectorAll('[data-count-up]').forEach(el => animateCountUp(el));
}

// 누계 평점 진행률 바 — 로딩 시 0%에서 목표치까지 채워지는 애니메이션
function initProgressBars() {
  document.querySelectorAll('.kpi-progress-fill').forEach(el => {
    const target = el.style.width;
    if (!target) return;
    el.style.width = '0%';
    requestAnimationFrame(() => requestAnimationFrame(() => {
      el.style.width = target;
    }));
  });
}

// Init
document.addEventListener('DOMContentLoaded', () => {
  updateNotifBadge();
  initToasts();
  restoreScrollPosition();
  initThemeToggle();
  initCountUps();
  initProgressBars();
});