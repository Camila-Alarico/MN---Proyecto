// Retroalimentación visual común a todo el sitio: barra de carga, avisos, validación de campos,
// resaltado de valores que cambian, avance de lectura y botón para volver arriba.
// Es un script clásico (sin dependencias) que publica `window.NumLearnFeedback`.
(() => {
  const doc = document, root = doc.documentElement;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const make = (tag, props = {}, parent = doc.body) => { const el = Object.assign(doc.createElement(tag), props); parent.append(el); return el; };

  // --- Barra de carga: navegación y peticiones al servidor ---------------------------------
  const bar = make('div', {id: 'fx-progress'});
  bar.setAttribute('aria-hidden', 'true');
  make('span', {}, bar);
  let pending = 0, hideTimer;
  const progress = {
    start() { pending++; clearTimeout(hideTimer); bar.classList.add('is-active'); },
    done() { pending = Math.max(0, pending - 1); if (!pending) hideTimer = setTimeout(() => bar.classList.remove('is-active'), 180); },
  };
  doc.addEventListener('click', event => {
    const link = event.target.closest?.('a[href]');
    if (!link || event.defaultPrevented || event.button || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    if (link.target === '_blank' || link.hasAttribute('download')) return;
    const url = new URL(link.href, location.href);
    if (url.origin !== location.origin || (url.pathname === location.pathname && url.search === location.search)) return;
    setTimeout(() => { if (!event.defaultPrevented) { progress.start(); setTimeout(progress.done, 8000); } }, 0);
  });
  doc.addEventListener('submit', event => {
    setTimeout(() => { if (!event.defaultPrevented) { progress.start(); setTimeout(progress.done, 8000); } }, 0);
  });
  addEventListener('pageshow', () => { pending = 0; bar.classList.remove('is-active'); });

  // --- Avisos emergentes -----------------------------------------------------------------------
  const toasts = make('div', {className: 'fx-toasts'});
  toasts.setAttribute('role', 'status');
  toasts.setAttribute('aria-live', 'polite');
  const icons = {success: 'bi-check-circle-fill', error: 'bi-exclamation-octagon-fill', info: 'bi-info-circle-fill'};
  function toast(message, kind = 'info', duration = 3800) {
    const repeated = [...toasts.children].find(item => item.dataset.message === message);
    if (repeated) repeated.remove();
    const item = make('div', {className: `fx-toast is-${kind}`}, toasts);
    item.dataset.message = message;
    make('i', {className: `fx-toast-icon bi ${icons[kind] || icons.info}`}, item).setAttribute('aria-hidden', 'true');
    make('span', {textContent: message}, item);
    const close = make('button', {type: 'button', textContent: '×'}, item);
    close.setAttribute('aria-label', 'Cerrar aviso');
    const dismiss = () => { if (!item.isConnected) return; item.classList.add('is-leaving'); setTimeout(() => item.remove(), reduced ? 0 : 220); };
    close.addEventListener('click', dismiss);
    if (duration) setTimeout(dismiss, duration);
    return item;
  }

  // --- Peticiones: el botón pulsado muestra que está trabajando ---------------------------------
  let lastButton = null, lastButtonTime = 0;
  doc.addEventListener('click', event => {
    const button = event.target.closest?.('button, .btn');
    if (button) { lastButton = button; lastButtonTime = performance.now(); }
  }, true);
  const nativeFetch = window.fetch;
  if (nativeFetch) {
    window.fetch = function (...args) {
      const button = lastButton && performance.now() - lastButtonTime < 500 && lastButton.classList.contains('btn') ? lastButton : null;
      lastButton = null;
      progress.start();
      button?.classList.add('fx-busy');
      const settle = () => { progress.done(); button?.classList.remove('fx-busy'); };
      return nativeFetch.apply(this, args).then(response => {
        settle();
        if (response.status === 429) toast('Demasiadas solicitudes seguidas. Espera un momento y vuelve a intentarlo.', 'error');
        else if (response.status >= 500) toast('El servidor no pudo completar la operación. Inténtalo nuevamente.', 'error');
        return response;
      }, error => {
        settle();
        if (error?.name !== 'AbortError') toast('No hay conexión con el servidor. Revisa que siga en ejecución.', 'error', 6000);
        throw error;
      });
    };
  }
  // Copiar al portapapeles: confirmación visible.
  const clipboard = navigator.clipboard;
  if (clipboard?.writeText) {
    const write = clipboard.writeText.bind(clipboard);
    clipboard.writeText = text => write(text).then(result => { toast('Copiado al portapapeles.', 'success', 2200); return result; });
  }

  // --- Campos: error visible junto al control ----------------------------------------------------
  doc.addEventListener('invalid', event => {
    const field = event.target;
    if (!field.matches?.('input, select, textarea')) return;
    field.classList.remove('fx-invalid');
    void field.offsetWidth;
    field.classList.add('fx-invalid');
    let note = field.parentElement?.querySelector(':scope > .fx-field-note');
    if (!note && field.parentElement) { note = doc.createElement('small'); note.className = 'fx-field-note'; field.insertAdjacentElement('afterend', note); }
    if (note) note.textContent = field.validationMessage;
  }, true);
  doc.addEventListener('input', event => {
    const field = event.target;
    if (!field.classList?.contains('fx-invalid') || !field.checkValidity()) return;
    field.classList.remove('fx-invalid');
    field.parentElement?.querySelector(':scope > .fx-field-note')?.remove();
  });

  // --- Un resultado que cambia se ilumina un instante ---------------------------------------------
  const main = doc.getElementById('main');
  function flash(element) {
    if (reduced || !element?.isConnected || element.closest('.lab, .fx-toasts, [data-no-flash]')) return;
    element.classList.remove('fx-updated');
    void element.offsetWidth;
    element.classList.add('fx-updated');
  }
  function watchChanges() {
    if (!main || !window.MutationObserver) return;
    const selector = '.status, .result-verdict, .error-results strong, #result-summary, output';
    const seen = new WeakMap();
    const observer = new MutationObserver(records => {
      const targets = new Set();
      for (const record of records) {
        const node = record.target.nodeType === 1 ? record.target : record.target.parentElement;
        const target = node?.closest?.(selector);
        if (target) targets.add(target);
      }
      targets.forEach(target => {
        const text = target.textContent;
        if (seen.get(target) === text) return;
        seen.set(target, text);
        flash(target);
      });
    });
    observer.observe(main, {subtree: true, childList: true, characterData: true});
    // El mensaje de error del formulario se acerca a la vista cuando aparece.
    const alert = doc.getElementById('alert');
    if (alert) new MutationObserver(() => {
      if (alert.hidden || !alert.textContent.trim()) return;
      const box = alert.getBoundingClientRect();
      if (box.top < 70 || box.bottom > innerHeight) alert.scrollIntoView({block: 'center', behavior: reduced ? 'auto' : 'smooth'});
    }).observe(alert, {attributes: true, childList: true, characterData: true, subtree: true});
  }
  // Se espera a que la página termine de pintarse para no resaltar los valores iniciales.
  if (doc.readyState === 'complete') setTimeout(watchChanges, 900);
  else addEventListener('load', () => setTimeout(watchChanges, 900));

  // --- Avance de lectura y volver arriba -----------------------------------------------------------
  const reading = make('div', {id: 'fx-reading'});
  reading.setAttribute('aria-hidden', 'true');
  const readingBar = make('span', {}, reading);
  const top = make('button', {id: 'fx-top', type: 'button', innerHTML: '<span aria-hidden="true">↑</span>'});
  top.setAttribute('aria-label', 'Volver al inicio de la página');
  top.addEventListener('click', () => { scrollTo({top: 0, behavior: reduced ? 'auto' : 'smooth'}); doc.getElementById('main')?.focus({preventScroll: true}); });
  let ticking = false;
  function onScroll() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      ticking = false;
      const range = root.scrollHeight - innerHeight;
      readingBar.style.setProperty('--read', range > innerHeight * 0.6 ? Math.min(1, scrollY / range).toFixed(4) : 0);
      top.classList.toggle('is-visible', scrollY > 700);
    });
  }
  addEventListener('scroll', onScroll, {passive: true});
  addEventListener('resize', onScroll);
  onScroll();

  // --- Temario: la unidad visible se marca en el índice superior ------------------------------------
  const unitLinks = [...doc.querySelectorAll('.unit-index-item')];
  if (unitLinks.length && window.IntersectionObserver) {
    const byId = new Map(unitLinks.map(link => [link.hash.slice(1), link]));
    const visible = new Set();
    const spy = new IntersectionObserver(entries => {
      entries.forEach(entry => entry.isIntersecting ? visible.add(entry.target.id) : visible.delete(entry.target.id));
      const current = [...byId.keys()].find(id => visible.has(id));
      unitLinks.forEach(link => link.classList.toggle('is-active', link.hash.slice(1) === current));
    }, {rootMargin: '-25% 0px -55% 0px'});
    byId.forEach((_, id) => { const section = doc.getElementById(id); if (section) spy.observe(section); });
  }

  window.NumLearnFeedback = {toast, progress, flash};
})();
