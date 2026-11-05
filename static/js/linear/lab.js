import {post, showError, busy, plot, line, table, format, typeset} from '../nonlinear/common.js';

const root = document.getElementById('lab');
const {mode, endpoint} = root.dataset;
const examples = JSON.parse(document.getElementById('linear-examples').textContent);
const form = document.getElementById('lab-form');
const grid = document.getElementById('matrix-grid');
const sizeSelect = document.getElementById('size');
const results = document.getElementById('lab-results');
const MAX = 3;
let revision = 0;
let pendingRequest = null;

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}
const sub = i => 'x' + String(i + 1).replace(/\d/g, d => '₀₁₂₃₄₅₆₇₈₉'[d]);

// --- Entrada ---------------------------------------------------------------
function input(id, label, value) {
  const field = el('input');
  Object.assign(field, {id, type: 'number', step: 'any', value: value ?? 0, required: true});
  field.setAttribute('aria-label', label);
  return field;
}

function build(n, matrix, vector) {
  grid.replaceChildren();
  grid.style.gridTemplateColumns = `repeat(${n}, minmax(0, 1fr)) 14px minmax(0, 1fr)`;
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) grid.append(input(`a-${i}-${j}`, `A fila ${i + 1}, columna ${j + 1}`, matrix?.[i]?.[j]));
    grid.append(el('span', 'matrix-sep', '|'));
    grid.append(input(`b-${i}`, `b fila ${i + 1}`, vector?.[i]));
  }
  sizeSelect.value = String(n);
  document.getElementById('size-note').textContent = `Tamaño n = ${n}: ${n} ecuaciones y ${n} incógnitas.`;
  document.getElementById('system-meaning').textContent =
    `Aquí n = ${n}: hay ${n} incógnitas (${Array.from({length: n}, (_, i) => sub(i)).join(', ')}) y ${n} observaciones.`;
}

function read() {
  const n = Number(sizeSelect.value);
  const value = id => {
    const text = document.getElementById(id).value.trim();
    if (text === '') throw new Error('Completa todos los campos con números.');
    return Number(text);
  };
  const payload = {size: n,
    matrix: Array.from({length: n}, (_, i) => Array.from({length: n}, (_, j) => value(`a-${i}-${j}`))),
    vector: Array.from({length: n}, (_, i) => value(`b-${i}`))};
  if (mode !== 'gauss') {
    payload.tolerance = Number(document.getElementById('tolerance').value);
    payload.max_iterations = Number(document.getElementById('max_iterations').value);
  }
  return payload;
}

function load(example) {
  build(example.size, example.matrix, example.vector);
}

// --- Salida ----------------------------------------------------------------
function matrixTable(rows, pivot = null) {
  const t = el('table', 'matrix');
  t.setAttribute('role', 'table');
  rows.forEach((row, i) => {
    const tr = t.insertRow();
    row.forEach((v, j) => {
      const td = tr.insertCell();
      td.textContent = format(v);
      if (j === row.length - 1) td.className = 'aug';
      if (pivot && pivot[0] === i && pivot[1] === j) td.className += ' pivot';
    });
  });
  return t;
}

function warnings(list, danger = false) {
  if (!list?.length) return null;
  const box = el('div', 'lab-warnings' + (danger ? ' lab-error' : ''));
  box.setAttribute('role', 'alert');
  list.forEach(text => box.append(el('p', '', text)));
  return box;
}

function metrics(items) {
  const box = el('div', 'lab-metrics');
  items.forEach(([label, value]) => {
    const d = el('div'); d.append(el('span', '', label), el('strong', '', value)); box.append(d);
  });
  return box;
}

const vec = v => '(' + v.map(format).join(', ') + ')';

function renderGauss(r, matrix, vector) {
  const box = el('section', 'panel');
  box.append(el('h2', '', 'Eliminación gaussiana con pivoteo parcial'));
  box.append(el('p', 'input-help', r.criterion));
  box.append(el('h4', '', 'Matriz aumentada inicial [A | b]'), matrixTable(r.augmented));
  r.steps.forEach(s => {
    const block = el('div', 'step-block');
    block.append(el('h4', '', `Columna ${s.column}: pivote ${format(s.pivot)} (fila ${s.pivot_row})`));
    if (s.swap) {
      block.append(el('p', '', `Intercambio de filas F${s.swap.from} ↔ F${s.swap.to} (el mayor |pivote| estaba en F${s.swap.to}).`),
        matrixTable(s.after_swap, [s.column - 1, s.column - 1]));
    } else block.append(el('p', '', 'Sin intercambio de filas.'));
    if (s.multipliers.length) {
      block.append(el('p', '', 'Multiplicadores: ' + s.multipliers.map(m => `m${m.row}${s.column} = ${format(m.value)}`).join(', ')),
        matrixTable(s.after, [s.column - 1, s.column - 1]));
    }
    box.append(block);
  });
  box.append(warnings(r.warnings, r.singular) ?? '');
  if (r.singular) { box.append(el('p', '', r.message)); return box; }
  box.append(el('h4', '', 'Sustitución hacia atrás'));
  const list = el('ul');
  r.back_substitution.forEach(b => list.append(el('li', '', `${b.formula} = ${format(b.value)}`)));
  box.append(list);
  box.append(solutionBlock(r, vector));
  return box;
}

function solutionBlock(r, vector) {
  const box = el('div');
  box.append(metrics([['Solución x', vec(r.solution)], ['Residuo r = b − A·x', vec(r.residual_vector)],
    ['‖r‖∞', format(r.residual)]]));
  const eq = el('table', 'table');
  eq.createCaption().textContent = 'Sustitución de la solución en cada ecuación';
  const head = eq.createTHead().insertRow();
  ['Ecuación', '(A·x)ᵢ', 'bᵢ', 'rᵢ'].forEach(h => { const th = el('th', '', h); th.scope = 'col'; head.append(th); });
  vector.forEach((b, i) => {
    const tr = eq.insertRow();
    [i + 1, b - r.residual_vector[i], b, r.residual_vector[i]].forEach(v => tr.insertCell().textContent = format(v));
  });
  const wrap = el('div', 'table-scroll');
  wrap.append(eq);
  box.append(wrap);
  return box;
}

function residualChart(parent, iterations, directResidual) {
  const target = el('div', 'plot');
  target.setAttribute('role', 'region');
  target.setAttribute('aria-label', 'Residuo por iteración');
  parent.append(el('p', 'input-help', 'Residuo ‖b − A·x‖∞ por iteración (escala logarítmica; un residuo cero no se dibuja).'), target);
  const rows = iterations.filter(row => row.residual > 0);
  const traces = [line(rows.map(r => r.n), rows.map(r => r.residual), 'Gauss-Seidel', {mode: 'lines+markers'})];
  if (directResidual > 0 && iterations.length) {
    traces.push(line([0, iterations[iterations.length - 1].n], [directResidual, directResidual], 'Eliminación gaussiana',
      {line: {dash: 'dash', width: 2}}));
  }
  return plot(target, traces, {xaxis: {title: 'Iteración'}, yaxis: {title: '‖r‖∞', type: 'log'}});
}

function renderSeidel(r, n) {
  const box = el('section', 'panel');
  box.append(el('h2', '', 'Gauss-Seidel desde el vector cero'));
  if (!r.iterations.length) { box.append(el('p', '', r.message)); return {box}; }
  box.append(el('p', 'notice', r.convergence_note));
  if (r.dominance) {
    box.append(el('p', 'input-help', 'Dominancia diagonal por filas (|aᵢᵢ| > Σ|aᵢⱼ|): ' +
      r.dominance.rows.map(d => `F${d.row}: ${format(d.diagonal)} ${d.strict ? '>' : '≤'} ${format(d.off_diagonal)}`).join(' · ')));
  }
  const columns = [['n', 'n'], ...Array.from({length: n}, (_, i) => [`x${i}`, sub(i)]), ['step', 'Paso ‖Δx‖∞'], ['residual', 'Residuo ‖r‖∞']];
  const rows = r.iterations.map(it => ({n: it.n, step: it.step, residual: it.residual,
    ...Object.fromEntries(it.x.map((v, i) => [`x${i}`, v]))}));
  const holder = el('div', 'table-scroll');
  box.append(holder);
  table(holder, columns, rows);
  box.append(el('p', 'status ' + (r.converged ? 'status-success' : 'status-warning'), `${r.status}: ${r.message} (${r.iterations_count} iteraciones)`));
  return {box, after: () => residualChart(box, r.iterations, null)};
}

async function render(r, payload) {
  results.replaceChildren();
  const n = payload.size;
  const tasks = [];
  if (mode === 'gauss') results.append(renderGauss(r, payload.matrix, payload.vector));
  else if (mode === 'seidel') {
    if (r.status === 'Sistema singular') results.append(warnings([r.message], true));
    const s = renderSeidel(r, n); results.append(s.box); if (s.after) tasks.push(s.after);
  } else {
    const {direct, iterative} = r;
    const cmp = el('section', 'panel');
    cmp.append(el('h2', '', 'Comparación'));
    cmp.append(warnings(direct.warnings, direct.singular) ?? '');
    const t = el('table', 'table');
    const head = t.createTHead().insertRow();
    ['Aspecto', 'Eliminación gaussiana', 'Gauss-Seidel'].forEach(h => { const th = el('th', '', h); th.scope = 'col'; head.append(th); });
    const row = (a, b, c) => { const tr = t.insertRow(); [a, b, c].forEach(v => tr.insertCell().textContent = v); };
    row('Solución', direct.solution ? vec(direct.solution) : 'No hay solución única',
      iterative.solution ? vec(iterative.solution) : iterative.status);
    row('Residuo ‖r‖∞', direct.residual == null ? '—' : format(direct.residual),
      iterative.residual == null ? '—' : format(iterative.residual));
    row('Procedimiento', `${direct.steps.length} pasos de eliminación, ${direct.swaps} intercambio(s) de filas`,
      `${iterative.iterations_count} iteraciones (${iterative.status})`);
    row('Diferencia ‖x_G − x_S‖∞', r.difference_inf == null ? '—' : format(r.difference_inf), '');
    const wrap = el('div', 'table-scroll'); wrap.append(t); cmp.append(wrap);
    r.notes.forEach(text => cmp.append(el('p', 'notice', text)));
    results.append(cmp);
    const s = renderSeidel(iterative, n);
    results.append(s.box);
    if (iterative.iterations.length) tasks.push(() => residualChart(s.box, iterative.iterations, direct.residual));
    const details = el('details', 'disclosure');
    details.append(el('summary', '', 'Ver el procedimiento paso a paso de la eliminación gaussiana'), renderGauss(direct, payload.matrix, payload.vector));
    results.append(details);
  }
  for (const task of tasks) await task();
  await typeset(results);
}

// --- Eventos ---------------------------------------------------------------
function invalidateResults() {
  revision += 1;
  pendingRequest?.abort();
  pendingRequest = null;
  busy(document.getElementById('execute'), false);
  showError('');
  results.replaceChildren(el('p', 'notice', 'Los datos cambiaron. Pulsa «Resolver» para actualizar el resultado.'));
}

form.addEventListener('input', invalidateResults);
form.addEventListener('change', invalidateResults);
Object.entries(examples).forEach(([key, ex]) => {
  const option = el('option', '', ex.title); option.value = key; document.getElementById('example').append(option);
});
document.getElementById('example').addEventListener('change', event => {
  if (event.target.value) load(examples[event.target.value]);
  showError('');
});
sizeSelect.addEventListener('change', () => {
  const n = Number(sizeSelect.value);
  const old = Array.from({length: MAX}, (_, i) => Array.from({length: MAX}, (_, j) => document.getElementById(`a-${i}-${j}`)?.value ?? 0));
  const oldB = Array.from({length: MAX}, (_, i) => document.getElementById(`b-${i}`)?.value ?? 0);
  build(n, old, oldB);
});
form.addEventListener('submit', async event => {
  event.preventDefault();
  const button = document.getElementById('execute');
  const requestRevision = ++revision;
  pendingRequest?.abort();
  pendingRequest = new AbortController();
  showError('');
  busy(button, true);
  results.replaceChildren(el('p', 'notice', 'Calculando…'));
  try {
    const payload = read();
    const answer = await post(endpoint, payload, pendingRequest.signal);
    if (requestRevision !== revision) return;
    await render(answer, payload);
  } catch (error) {
    if (requestRevision === revision && error.name !== 'AbortError') {
      results.replaceChildren(el('p', 'notice', 'Revisa los datos y vuelve a pulsar «Resolver».'));
      showError(error.message);
    }
  } finally {
    if (requestRevision === revision) {
      pendingRequest = null;
      busy(button, false);
    }
  }
});

// Selector de método (directo/iterativo): lleva a la URL canónica del método elegido con el sistema actual.
document.getElementById('method-select')?.addEventListener('change', event => {
  const slug = event.target.value;
  if (!slug) return;
  const params = new URLSearchParams();
  try {
    const {matrix, vector} = read();
    params.set('matrix', JSON.stringify(matrix));
    params.set('vector', JSON.stringify(vector));
  } catch { /* campos incompletos: el destino carga el caso base */ }
  location.assign(`/sistemas-lineales/${slug}/?${params}`);
});

// Datos iniciales: ?matrix=[[...]]&vector=[...] (enlaces del historial) o el caso base.
const query = new URLSearchParams(location.search);
try {
  const matrix = JSON.parse(query.get('matrix') || 'null'), vector = JSON.parse(query.get('vector') || 'null');
  if (Array.isArray(matrix) && Array.isArray(vector) && [2, 3].includes(matrix.length)) build(matrix.length, matrix, vector);
  else load(examples.base);
} catch { load(examples.base); }
