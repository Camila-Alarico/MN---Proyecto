import {post, showError, plot, line, points, table, format, setMath, typeset, busy} from './common.js';

const form = document.getElementById('compare-form');
const registry = JSON.parse(document.getElementById('method-registry').textContent);
let generation = 0, controller = null;

const selected = () => Array.from(form.querySelectorAll('[name=methods]:checked')).map(input => input.value);

function configure() {
  const required = new Set(selected().flatMap(key => registry[key].parameters));
  if (selected().includes('fixed-point')) required.add('g');
  document.querySelectorAll('[data-compare-param]').forEach(el => {
    const active = required.has(el.dataset.compareParam);
    el.hidden = !active;
    el.querySelector('input').disabled = !active;
    el.querySelector('input').required = active;
  });
}

form.elements.g.value = '(x + 2)^0.3333333333333333';
form.querySelectorAll('[name=methods]').forEach(input => input.addEventListener('change', configure));
configure();

function resetPanels(message) {
  document.getElementById('comparison-cards').replaceChildren();
  document.getElementById('comparison-table').replaceChildren();
  document.getElementById('convergence-panels').replaceChildren();
  document.getElementById('propagation-table').replaceChildren();
  document.getElementById('propagation-panel').hidden = true;
  document.getElementById('reference-panel').hidden = true;
  const graph = document.getElementById('comparison-plot');
  if (window.Plotly && graph.data) window.Plotly.purge(graph);
  graph.textContent = message;
}

form.addEventListener('input', () => {
  generation++;
  controller?.abort();
  busy(form.querySelector('button'), false);
  resetPanels('Datos actualizados. Ejecuta una nueva comparación.');
  showError('');
});

function statusLabel(verdict) {
  return {converge: 'Converge', diverge: 'Diverge'}[verdict] || 'No concluyente';
}
function statusClass(verdict) {
  return {converge: 'status-success', diverge: 'status-danger'}[verdict] || 'status-warning';
}

function convergencePanel(entry) {
  const conv = entry.convergence;
  const article = document.createElement('article');
  article.className = 'panel';
  const title = document.createElement('h3');
  title.textContent = entry.title;
  const status = document.createElement('span');
  status.className = `status ${statusClass(conv?.verdict)}`;
  status.textContent = statusLabel(conv?.verdict);
  article.append(title, status);

  if (!conv) {
    const p = document.createElement('p');
    p.textContent = entry.message || 'No se pudo analizar la convergencia.';
    article.append(p);
    return article;
  }

  const criterion = document.createElement('p');
  criterion.className = 'math-block';
  setMath(criterion, conv.criterion_tex, 'Criterio');
  const formula = document.createElement('p');
  formula.className = 'math-block';
  setMath(formula, conv.formula_tex, 'Fórmula');
  const text = document.createElement('p');
  text.textContent = conv.text;
  article.append(criterion, formula, text);

  if (conv.lambda != null) {
    const lam = document.createElement('p');
    lam.textContent = `|φ′| ${conv.lambda_at ? conv.lambda_at + ' = ' : '= '}${format(conv.lambda)}`;
    article.append(lam);
  }
  if (conv.order) {
    const order = document.createElement('p');
    order.textContent = `Orden de convergencia: ${conv.order.label}.`;
    article.append(order);
  }

  // Curva |phi'(x)| con la línea y=1: por encima diverge, por debajo converge.
  if (conv.curve) {
    const plotDiv = document.createElement('div');
    plotDiv.className = 'plot';
    article.append(plotDiv);
    const traces = [
      line(conv.curve.x, conv.curve.y, "|φ′(x)|"),
      line([conv.curve.x[0], conv.curve.x[conv.curve.x.length - 1]], [1, 1], 'y = 1 (frontera)', {line: {dash: 'dash'}}),
    ];
    const iterX = conv.iterates.filter(p => p.y != null).map(p => p.x);
    const iterY = conv.iterates.filter(p => p.y != null).map(p => p.y);
    if (iterX.length) traces.push(points(iterX, iterY, 'Iterados'));
    plot(plotDiv, traces, {
      xaxis: {title: 'x'},
      yaxis: {title: '|φ′(x)| (recortado en 4 para dibujar)', range: [0, conv.curve.clamp]},
    });
  }

  if (conv.checks?.length) {
    const list = document.createElement('ul');
    list.className = 'check-list';
    conv.checks.forEach(check => {
      const item = document.createElement('li');
      item.className = check.ok === true ? 'check-ok' : check.ok === false ? 'check-fail' : 'check-unknown';
      item.textContent = `${check.ok === true ? '✓' : check.ok === false ? '✕' : '·'} ${check.label}: ${check.detail}`;
      list.append(item);
    });
    article.append(list);
  }
  return article;
}

form.addEventListener('submit', async event => {
  event.preventDefault();
  const seq = ++generation;
  controller?.abort();
  controller = new AbortController();
  const keys = selected();
  if (!keys.length) { showError('Selecciona al menos un método.'); return; }
  showError('');
  const button = form.querySelector('button');
  busy(button, true);
  const values = Object.fromEntries(new FormData(form));

  let data;
  try {
    data = await post('/api/nonlinear/compare/', {...values, methods: keys}, controller.signal);
  } catch (error) {
    if (seq !== generation || error.name === 'AbortError') return;
    showError(error.message);
    busy(button, false);
    return;
  }
  if (seq !== generation) return;

  // --- Referencia ---
  const refPanel = document.getElementById('reference-panel'), refText = document.getElementById('reference-text');
  refPanel.hidden = false;
  refText.textContent = data.reference.root == null
    ? 'No se pudo estimar una raíz de referencia con estos datos.'
    : `x* ≈ ${format(data.reference.root)} (${data.reference.source}). `
      + `κ(x*) = 1/|f′(x*)| ${format(data.reference.condition_number)}. `
      + (data.reference.multiple_root ? 'f′(x*) ≈ 0: es una raíz múltiple; el error amplifica mucho al residuo.' : '');

  // --- Tarjetas por método ---
  const cards = document.getElementById('comparison-cards');
  cards.replaceChildren();
  const rows = [], traces = [];
  data.methods.forEach(entry => {
    const card = document.createElement('article');
    card.className = 'panel';
    const title = document.createElement('h3');
    title.textContent = entry.title;
    const status = document.createElement('span');
    status.className = `status ${entry.converged ? 'status-success' : 'status-warning'}`;
    status.textContent = entry.converged ? 'Convergió' : 'No convergió';
    const details = document.createElement('p');
    details.textContent = `Aproximación: ${format(entry.root)} · ${entry.iterations_count} iteraciones · `
      + `Error absoluto: ${format(entry.final?.absolute)} · Residuo: ${format(entry.final?.residual)} · ${format(entry.elapsed_ms)} ms`;
    const message = document.createElement('p');
    message.textContent = entry.message || '';
    card.append(title, status, details, message);
    cards.append(card);

    rows.push({
      method: entry.title, root: entry.root, iterations: entry.iterations_count,
      absolute: entry.final?.absolute, residual: entry.final?.residual, converged: entry.converged ? 'Sí' : 'No',
      order: entry.summary?.observed_order != null ? format(entry.summary.observed_order) : entry.summary?.theoretical_label,
      to_tolerance: entry.summary?.iterations_to_tolerance?.error ?? '—',
    });
    const xs = entry.rows.map(r => r.n), ys = entry.rows.map(r => r.absolute > 0 ? r.absolute : null);
    if (xs.length) traces.push(line(xs, ys, entry.title));
  });

  table(document.getElementById('comparison-table'),
    [['method', 'Método'], ['root', 'Aproximación'], ['iterations', 'Iteraciones'], ['absolute', 'Error absoluto'],
     ['residual', 'Residuo'], ['converged', 'Convergió'], ['order', 'Orden'], ['to_tolerance', 'Iteración que cumple τ']],
    rows);
  plot(document.getElementById('comparison-plot'), traces,
    {xaxis: {title: 'Iteración', dtick: 1}, yaxis: {title: 'Error absoluto (log)', type: 'log'}});

  // --- Convergencia / divergencia con fórmula ---
  const panels = document.getElementById('convergence-panels');
  panels.replaceChildren();
  data.methods.forEach(entry => panels.append(convergencePanel(entry)));
  await typeset(panels);

  // --- Propagación entre métodos ---
  const propPanel = document.getElementById('propagation-panel');
  if (data.propagation?.length) {
    propPanel.hidden = false;
    const propRows = data.propagation.map(p => ({
      pair: `${p.a} ↔ ${p.b}`, difference: p.difference, bound: p.bound,
      consistent: p.consistent ? 'Sí' : 'No, revisar',
    }));
    table(document.getElementById('propagation-table'),
      [['pair', 'Métodos'], ['difference', '|x_A − x_B|'], ['bound', 'Eₐ(A) + Eₐ(B)'], ['consistent', '¿Consistente?']],
      propRows);
  } else {
    propPanel.hidden = true;
  }

  busy(button, false);
});
