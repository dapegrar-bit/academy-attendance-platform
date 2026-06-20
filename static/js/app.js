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

  function showNotification(item){
    const card = document.createElement('div');
    card.className = 'live-notification-card';
    card.dataset.notificationId = item.id;
    card.innerHTML = `
      <button type="button" class="live-notification-close" aria-label="إغلاق">×</button>
      <div class="live-notification-icon">🔔</div>
      <div class="live-notification-content">
        <strong>${escapeHtml(item.title || 'تنبيه جديد')}</strong>
        <p>${escapeHtml(item.body || '')}</p>
        <small>${escapeHtml(item.created_at || '')}${item.session ? ' • ' + escapeHtml(item.session) : ''}</small>
      </div>
    `;
    stack.prepend(card);

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
    }, 14000);
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
        if(!data || !Array.isArray(data.notifications)) return;
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
        // نعلّم التنبيهات كمقروءة بعد وصولها للمتدرب حتى لا تتكرر كل مرة.
        if(deliveredIds.length){
          setTimeout(()=>markRead(deliveredIds), 1200);
        }
      })
      .catch(()=>{})
      .finally(()=>{ polling = false; });
  }

  // أول فحص بعد فتح الصفحة، ثم فحص خفيف كل 5 ثوانٍ بدون إعادة تحميل الصفحة.
  setTimeout(poll, 1200);
  setInterval(poll, 5000);

  document.addEventListener('visibilitychange', function(){
    if(!document.hidden) poll();
  });
}
