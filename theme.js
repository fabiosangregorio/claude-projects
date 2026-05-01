/* Theme toggle — shared across all pages.
   The data-theme attribute is set early via inline script in each page <head>
   to prevent flash. This file injects the toggle button and handles clicks. */
(function(){
  var SUN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/></svg>';
  var MOON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';

  function get(){ return document.documentElement.getAttribute('data-theme') || 'dark'; }

  function apply(t){
    document.documentElement.setAttribute('data-theme', t);
    var meta = document.querySelector('meta[name=theme-color]');
    if (meta) meta.setAttribute('content', t === 'light' ? '#ffffff' : '#0e1117');
  }

  function init(){
    var btn = document.createElement('button');
    btn.className = 'theme-toggle';
    btn.setAttribute('aria-label', 'Cambia tema');
    btn.innerHTML = get() === 'dark' ? SUN : MOON;
    btn.onclick = function(){
      var next = get() === 'dark' ? 'light' : 'dark';
      apply(next);
      try { localStorage.setItem('theme', next); } catch(e) {}
      btn.innerHTML = next === 'dark' ? SUN : MOON;
    };
    document.body.appendChild(btn);
    apply(get()); // sync meta theme-color on load
    window.addEventListener('storage', function(e){
      if (e.key === 'theme' && e.newValue) {
        apply(e.newValue);
        btn.innerHTML = e.newValue === 'dark' ? SUN : MOON;
      }
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
