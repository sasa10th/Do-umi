// ── Sidebar Toggle ────────────────────────────────
function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
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
      html = '<div class="search-item" style="color:#999">검색 결과가 없습니다.</div>';
    } else {
      data.penalties.forEach(p => {
        html += `<div class="search-item" onclick="location.href='/penalties'">
          <strong>벌점</strong> ${p.reason} <span style="color:#999;font-size:11px">${p.date}</span>
        </div>`;
      });
      data.documents.forEach(d => {
        html += `<div class="search-item" onclick="location.href='/documents'">
          <strong>천자문</strong> ${d.title} <span style="color:#999;font-size:11px">${d.due_date}</span>
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

// Auto-dismiss alerts after 5 sec
document.querySelectorAll('.alert').forEach(el => {
  setTimeout(() => {
    el.style.transition = 'opacity 0.4s';
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 400);
  }, 5000);
});

// Init
document.addEventListener('DOMContentLoaded', () => {
  updateNotifBadge();
});