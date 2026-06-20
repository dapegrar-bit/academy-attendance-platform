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
});
