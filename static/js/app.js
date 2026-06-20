document.addEventListener('DOMContentLoaded', function(){
  document.querySelectorAll('[data-tab]').forEach(function(btn){
    btn.addEventListener('click', function(){
      const tab = btn.dataset.tab;
      document.querySelectorAll('[data-tab]').forEach(b=>b.classList.remove('active'));
      document.querySelectorAll('.tab-pane').forEach(p=>p.classList.remove('active'));
      btn.classList.add('active');
      const pane = document.getElementById(tab);
      if(pane) pane.classList.add('active');
    });
  });

  initLiveNotifications();
});

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return '';
}

function initLiveNotifications(){
  const body = document.body;
  const pollUrl = body.dataset.notificationPollUrl;
  const readUrl = body.dataset.notificationReadUrl;
  const role = body.dataset.userRole;
  const stack = document.getElementById('live-notification-stack');

  if(!pollUrl || !stack || role !== 'trainee') return;

  const storageKey = 'academy_last_notification_id';
  let lastId = parseInt(localStorage.getItem(storageKey) || '0', 10) || 0;
  let polling = false;

  const instantPanel = document.createElement('div');
  instantPanel.id = 'instant-checkin-panel';
  instantPanel.className = 'instant-checkin-panel';
  document.body.appendChild(instantPanel);

  function checkIn(url){
    if(!url) return;
    fetch(url, {
      method: 'POST',
      headers: {'X-CSRFToken': getCookie('csrftoken')},
      credentials: 'same-origin',
      cache: 'no-store'
    })
      .then(function(){ window.location.href = '/panel/trainee/'; })
      .catch(function(){ window.location.href = url; });
  }

  function renderInstantPanel(items){
    if(!Array.isArray(items) || !items.length){
      instantPanel.classList.remove('show');
      instantPanel.innerHTML = '';
      return;
    }
    instantPanel.innerHTML = `
      <div class="instant-checkin-card">
        <div class="instant-checkin-head">
          <span class="instant-checkin-icon">⚡</span>
          <div>
            <strong>حضور فجائي متاح الآن</strong>
            <p>اضغطي على زر التحضير لتسجيل حضورك فورًا.</p>
          </div>
        </div>
        <div class="instant-checkin-list"></div>
      </div>
    `;
    const list = instantPanel.querySelector('.instant-checkin-list');
    items.forEach(function(item){
      const row = document.createElement('div');
      row.className = 'instant-checkin-row';
      row.innerHTML = `
        <div>
          <strong>${escapeHtml(item.title || 'محاضرة')}</strong>
          <small>${escapeHtml(item.date || '')}${item.time ? ' • ' + escapeHtml(item.time) : ''}</small>
        </div>
        <button type="button" class="instant-circle-action" data-checkin-url="${escapeHtml(item.checkin_url || '')}">تحضير الآن</button>
      `;
      list.appendChild(row);
    });
    instantPanel.querySelectorAll('[data-checkin-url]').forEach(function(btn){
      btn.addEventListener('click', function(){
        btn.disabled = true;
        btn.textContent = 'جاري التسجيل...';
        checkIn(btn.dataset.checkinUrl);
      });
    });
    instantPanel.classList.add('show');
  }

  function showNotification(item){
    const card = document.createElement('div');
    card.className = 'live-notification-card';
    card.dataset.notificationId = item.id;
    const actionHtml = item.checkin_url ? `<button type="button" class="live-checkin-btn" data-checkin-url="${escapeHtml(item.checkin_url)}">⚡ تحضير فجائي الآن</button>` : '';
    card.innerHTML = `
      <button type="button" class="live-notification-close" aria-label="إغلاق">×</button>
      <div class="live-notification-icon">🔔</div>
      <div class="live-notification-content">
        <strong>${escapeHtml(item.title || 'تنبيه جديد')}</strong>
        <p>${escapeHtml(item.body || '')}</p>
        <small>${escapeHtml(item.created_at || '')}${item.session ? ' • ' + escapeHtml(item.session) : ''}</small>
        ${actionHtml}
      </div>
    `;
    stack.prepend(card);

    const action = card.querySelector('.live-checkin-btn');
    if(action){
      action.addEventListener('click', function(){
        action.disabled = true;
        action.textContent = 'جاري التسجيل...';
        checkIn(action.dataset.checkinUrl);
      });
    }

    const close = card.querySelector('.live-notification-close');
    close.addEventListener('click', function(){
      markRead([item.id]);
      card.classList.add('hide');
      setTimeout(()=>card.remove(), 250);
    });

    setTimeout(function(){
      if(document.body.contains(card)){
        card.classList.add('hide');
        setTimeout(()=>card.remove(), 250);
      }
    }, 18000);
  }

  function escapeHtml(value){
    return String(value).replace(/[&<>'"]/g, function(ch){
      return ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'})[ch];
    });
  }

  function markRead(ids){
    if(!readUrl || !ids || !ids.length) return;
    const form = new FormData();
    ids.forEach(id => form.append('ids[]', id));
    fetch(readUrl, {
      method: 'POST',
      headers: {'X-CSRFToken': getCookie('csrftoken')},
      body: form,
      credentials: 'same-origin'
    }).catch(()=>{});
  }

  function poll(){
    if(polling || document.hidden) return;
    polling = true;
    const url = new URL(pollUrl, window.location.origin);
    if(lastId) url.searchParams.set('last_id', lastId);

    fetch(url.toString(), {credentials: 'same-origin', cache: 'no-store'})
      .then(res => res.ok ? res.json() : null)
      .then(data => {
        if(!data) return;
        renderInstantPanel(data.open_checkins || []);
        if(!Array.isArray(data.notifications)) return;
        const deliveredIds = [];
        data.notifications.forEach(item => {
          if(item.id && item.id > lastId){
            lastId = item.id;
            localStorage.setItem(storageKey, String(lastId));
          }
          if(item.id){
            deliveredIds.push(item.id);
            showNotification(item);
          }
        });
        if(deliveredIds.length){
          setTimeout(()=>markRead(deliveredIds), 1200);
        }
      })
      .catch(()=>{})
      .finally(()=>{ polling = false; });
  }

  setTimeout(poll, 900);
  setInterval(poll, 5000);

  document.addEventListener('visibilitychange', function(){
    if(!document.hidden) poll();
  });
}
