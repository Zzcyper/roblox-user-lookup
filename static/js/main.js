const STORAGE_KEY = 'rolookup_recents';
const MAX_RECENTS = 8;

function getRecents() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY)) || []; } catch { return []; }
}

function saveRecentSearch(user) {
    const list = getRecents();
    const idx = list.findIndex(r => r.username.toLowerCase() === user.username.toLowerCase());
    if (idx > -1) list.splice(idx, 1);
    list.unshift(user);
    if (list.length > MAX_RECENTS) list.pop();
    localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
    renderRecents();
}

function clearRecents() {
    localStorage.removeItem(STORAGE_KEY);
    renderRecents();
}

function renderRecents() {
    const section = document.getElementById('recentSection');
    const grid = document.getElementById('recentGrid');
    if (!section || !grid) return;

    const list = getRecents();
    if (!list.length) { section.style.display = 'none'; return; }

    section.style.display = 'block';
    grid.innerHTML = list.map(u => `
    <div class="col-6 col-md-4 col-lg-3">
      <a href="/user/${esc(u.username)}" class="recent-card">
        ${u.avatar
          ? `<img src="${esc(u.avatar)}" class="recent-avatar" alt="${esc(u.username)}"
                  onerror="this.parentNode.innerHTML='<div class=\\'recent-placeholder\\'><i class=\\'fas fa-user\\'></i></div>'">`
          : `<div class="recent-placeholder"><i class="fas fa-user"></i></div>`}
        <div>
          <div style="font-weight:600;font-size:.87rem">${esc(u.username)}</div>
          ${u.displayName && u.displayName !== u.username
            ? `<div style="font-size:.73rem;color:var(--tx2)">${esc(u.displayName)}</div>`
            : ''}
        </div>
      </a>
    </div>
  `).join('');
}


function copyText(text, el) {
  const write = () => {
    if (el) {
      const orig = el.innerHTML;
      el.innerHTML = el.innerHTML.replace(/[\s\S]*/, '<i class="fas fa-check me-1"></i>Copied!');
      setTimeout(() => { el.innerHTML = orig; }, 1800);
    }
    showToast('Copied: ' + text);
  };

  if (navigator.clipboard) {
    navigator.clipboard.writeText(text).then(write).catch(() => fallbackCopy(text, write));
  } else {
    fallbackCopy(text, write);
  }
}

function fallbackCopy(text, cb) {
  const ta = document.createElement('textarea');
  ta.value = text;
  ta.style.cssText = 'position:fixed;opacity:0;top:0;left:0';
  document.body.appendChild(ta);
  ta.select();
  document.execCommand('copy');
  document.body.removeChild(ta);
  if (cb) cb();
}

let toastTimer;
function showToast(msg) {
  const el = document.getElementById('toastEl');
  if (!el) return;
  el.textContent = msg;
  el.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove('show'), 2400);
}


function shareProfile(username) {
  const url = window.location.href;
  if (navigator.share) {
    navigator.share({
      title: `${username} — RoLookup`,
      text:  `Check out ${username}'s Roblox profile on RoLookup!`,
      url,
    }).catch(() => {});
  } else {
    copyText(url, null);
    showToast('Profile URL copied to clipboard!');
  }
}

window.addEventListener('scroll', () => {
  const btn = document.getElementById('backToTop');
  if (btn) btn.classList.toggle('show', window.scrollY > 400);
});

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.search-suggest').forEach(btn => {
    btn.addEventListener('click', () => {
      const input = document.getElementById('mainSearch');
      if (input) { input.value = btn.dataset.username; input.closest('form').submit(); }
    });
  });

  document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', () => {
      const inp = form.querySelector('input[name="username"]');
      const btn = form.querySelector('button[type="submit"]');
      if (inp && inp.value.trim() && btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
      }
    });
  });

  renderRecents();
});

function esc(str) {
  const d = document.createElement('div');
  d.appendChild(document.createTextNode(String(str)));
  return d.innerHTML;
}