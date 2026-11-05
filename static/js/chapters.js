// The three previews stay readable as ordinary sections without JavaScript.
const explorer = document.querySelector('[data-chapter-explorer]');
if (explorer) {
  const navigation = explorer.querySelector('.chapter-tabs');
  const tabs = [...navigation.querySelectorAll('a')];
  const panels = tabs.map(tab => document.querySelector(tab.hash));
  const counter = explorer.querySelector('.chapter-position');
  navigation.setAttribute('role', 'tablist');
  tabs.forEach((tab, index) => {
    tab.setAttribute('role', 'tab');
    tab.setAttribute('aria-controls', panels[index].id);
    panels[index].setAttribute('role', 'tabpanel');
    panels[index].setAttribute('aria-labelledby', tab.id);
    panels[index].tabIndex = 0;
  });
  function select(index, focus = false) {
    tabs.forEach((tab, i) => {
      tab.setAttribute('aria-selected', String(i === index));
      tab.tabIndex = i === index ? 0 : -1;
      panels[i].hidden = i !== index;
    });
    counter.textContent = `${String(index + 1).padStart(2, '0')} — 03`;
    if (focus) tabs[index].focus({preventScroll: true});
  }
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', event => {event.preventDefault(); select(index);});
    tab.addEventListener('keydown', event => {
      const next = {ArrowRight: (index + 1) % tabs.length, ArrowLeft: (index + tabs.length - 1) % tabs.length, Home: 0, End: tabs.length - 1}[event.key];
      if (next === undefined) return;
      event.preventDefault(); select(next, true);
    });
  });
  select(Math.max(0, panels.findIndex(panel => `#${panel.id}` === location.hash)));
  window.addEventListener('hashchange', () => {
    const index = panels.findIndex(panel => `#${panel.id}` === location.hash);
    if (index >= 0) select(index);
  });
}
