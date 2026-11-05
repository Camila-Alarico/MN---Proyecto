// Mantiene enlaces utilizables sin JS y presenta una sección a la vez al activarse.
document.querySelectorAll('[data-method-tabs]').forEach(nav => {
  const tabs = [...nav.querySelectorAll('[data-panel]')];
  const panels = [...document.querySelectorAll('[data-method-panel]')];
  nav.setAttribute('role', 'tablist');
  tabs.forEach((tab, index) => {
    tab.id = `method-tab-${index}`;
    tab.setAttribute('role', 'tab');
    tab.setAttribute('aria-controls', tab.hash.slice(1));
    const panel = document.getElementById(tab.hash.slice(1));
    panel?.setAttribute('role', 'tabpanel');
    panel?.setAttribute('aria-labelledby', tab.id);
  });
  function select(tab, update = true) {
    tabs.forEach(item => {
      const active = item === tab;
      item.classList.toggle('selected', active);
      item.setAttribute('aria-selected', String(active));
      item.tabIndex = active ? 0 : -1;
    });
    panels.forEach(panel => {
      panel.hidden = panel.dataset.methodPanel !== tab.dataset.panel;
      if (!panel.hidden) panel.classList.add('method-panel-enter');
    });
    if (update) history.replaceState(null, '', tab.hash);
    window.dispatchEvent(new Event('resize'));
  }
  function fromLocation() {
    const selected = tabs.find(tab => tab.hash === location.hash)
      || (location.search ? tabs.find(tab => tab.dataset.panel === 'laboratory') : tabs[0]);
    select(selected, false);
  }
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', event => {event.preventDefault(); select(tab);});
    tab.addEventListener('keydown', event => {
      let next;
      if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
      if (event.key === 'ArrowLeft') next = (index + tabs.length - 1) % tabs.length;
      if (event.key === 'Home') next = 0;
      if (event.key === 'End') next = tabs.length - 1;
      if (next !== undefined) {event.preventDefault(); tabs[next].focus(); select(tabs[next]);}
    });
  });
  window.addEventListener('hashchange', fromLocation);
  fromLocation();
});
