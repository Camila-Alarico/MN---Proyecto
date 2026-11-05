import {simulatorUrls,  post, showError, table, plot, line, points, format, busy, setMath } from './common.js';
import { visualize, columns } from './visualizers.js';
import { buildCsv, configurationUrl } from './solver-export.js';

const root = document.getElementById('simulator');
const form = document.getElementById('solver-form');
const registry = JSON.parse(document.getElementById('method-registry').textContent);
const $ = id => document.getElementById(id);

let method = root.dataset.method;
let result = null;
let index = -1;
let timer = null;
let controller = null;
let generation = 0;
let graphController = null;
let graphVersion = 0;
let graphOverride = null;
let viewport = null;
let previewTimer;

// ---------------------------------------------------------------------------
// Estado
// ---------------------------------------------------------------------------

function stop() {
  clearInterval(timer);
  timer = null;
  $('auto').textContent = 'Modo automático';
}

function clearPlot(id, message) {
  if (window.Plotly && $(id).data) window.Plotly.purge($(id));
  $(id).textContent = message;
}

function invalidate() {
  generation++;
  controller?.abort();
  graphController?.abort();
  graphVersion++;
  stop();
  clearTimeout(previewTimer);
  result = null;
  index = -1;
  graphOverride = null;
  viewport = null;
  $('next').disabled = false;
  $('auto').disabled = false;
  $('previous').disabled = true;
  $('iteration-slider').disabled = true;
  $('export-csv').disabled = true;
  busy($('execute'), false);
  $('execute').textContent = 'Ejecutar';
  $('state').textContent = 'Listo para explorar';
  $('state').className = 'status';
  $('iterations').replaceChildren();
  $('iteration-count').textContent = '0 pasos';
  $('result-summary').textContent = 'Datos actualizados. Ejecuta para obtener un nuevo resultado.';
  $('explanation').textContent = 'Ejecuta el método o avanza una iteración.';
  $('explanation-formula').hidden = true;
  $('copy-feedback').textContent = '';
  $('derivatives').replaceChildren();
  clearPlot('plot', 'Actualizando vista…');
  $('convergence-plot').classList.remove('has-results');
  clearPlot('convergence-plot', 'Ejecuta para observar el residuo de cada paso.');
  showError('');
}

function configure() {
  const meta = registry[method];
  document.querySelectorAll('[data-param]').forEach(el => {
    const active = meta.parameters.includes(el.dataset.param);
    el.hidden = !active;
    el.querySelector('input').disabled = !active;
    el.querySelector('input').required = active;
  });
  $('expression-label').textContent = method === 'fixed-point' ? 'Función g(x)' : 'Función f(x)';
  $('method-description').textContent = meta.description;
  $('method-tip').textContent = meta.tip;
  $('assistant-message').textContent = meta.tip;
  setMath($('method-formula'), meta.formula, meta.formula);
}

// Ejes: el usuario manda (viewport); si no, el backend sugiere un rango Y que
// encuadra el intervalo/puntos del método en vez de toda la muestra.
function axes() {
  const base = { uirevision: `${generation}:${graphVersion}` };
  if (viewport) {
    return {
      ...base,
      xaxis: { title: 'x', range: viewport.x, zeroline: true },
      yaxis: { title: 'y', ...(viewport.y ? { range: viewport.y } : { autorange: true }), zeroline: true },
    };
  }
  if (result && !graphOverride && result.plot.y_range) {
    return { ...base, yaxis: { title: 'y', range: result.plot.y_range, zeroline: true } };
  }
  return base;
}

// ---------------------------------------------------------------------------
// Peticiones
// ---------------------------------------------------------------------------

async function preview(ranges = null) {
  graphController?.abort();
  graphController = new AbortController();
  const seq = ++graphVersion;
  const gen = generation;
  try {
    const graph = await post(
      '/api/nonlinear/graph/',
      { expression: form.elements.expression.value, a: ranges?.x[0] ?? -2, b: ranges?.x[1] ?? 3 },
      graphController.signal,
    );
    if (seq !== graphVersion || gen !== generation) return;
    showError('');
    viewport = ranges;
    if (result) {
      graphOverride = graph;
      render();
    } else {
      await plot($('plot'), [line(graph.x, graph.y, method === 'fixed-point' ? 'g(x)' : 'f(x)')], axes());
    }
  } catch (error) {
    if (seq === graphVersion && error.name !== 'AbortError') {
      showError(error.message);
      if (!result) clearPlot('plot', 'No hay una vista válida para esta expresión.');
    }
  }
}

async function calculate() {
  if (result) return true;
  if (!form.reportValidity()) return false;
  const seq = ++generation;
  controller?.abort();
  controller = new AbortController();
  graphController?.abort();
  graphVersion++;
  clearTimeout(previewTimer);
  busy($('execute'), true);
  $('next').disabled = true;
  $('auto').disabled = true;
  showError('');
  try {
    const answer = await post(`/api/nonlinear/${method}/`, Object.fromEntries(new FormData(form)), controller.signal);
    if (seq !== generation) return false;
    result = answer;
    graphOverride = null;
    viewport = null;
    $('range-min').value = answer.plot.x[0];
    $('range-max').value = answer.plot.x.at(-1);
    $('y-min').value = '';
    $('y-max').value = '';
    const deriv = [];
    if (result.derivative) deriv.push(`f'(x)=${result.derivative}`);
    if (result.second_derivative) deriv.push(`f''(x)=${result.second_derivative}`);
    setMath($('derivatives'), deriv.join(String.raw`\qquad `), deriv.join(' · '), {inline: true});
    if (method === 'fixed-point' && result.local_slope != null) {
      $('assistant-message').textContent = `|g′(x₀)| = ${format(result.local_slope)}. ${registry[method].tip}`;
    }
    $('export-csv').disabled = !result.iterations.length;
    return true;
  } catch (error) {
    if (seq === generation && error.name !== 'AbortError') showError(error.message);
    return false;
  } finally {
    if (seq === generation) {
      busy($('execute'), false);
      $('next').disabled = false;
      $('auto').disabled = false;
    }
  }
}

// ---------------------------------------------------------------------------
// Render
// ---------------------------------------------------------------------------

function selectStep(value) {
  stop();
  index = value;
  render();
}

function render() {
  if (!result) return;
  const row = result.iterations[index];
  const finished = index >= result.iterations.length - 1;
  const view = visualize(method, { ...result, plot: graphOverride || result.plot }, index);
  plot($('plot'), view.traces, { shapes: view.shapes, ...axes() });
  table($('iterations'), columns[method], result.iterations, index, step => {
    selectStep(step);
    $('iterations').querySelectorAll('button')[step]?.focus({ preventScroll: true });
  });
  $('iteration-count').textContent = `${Math.max(0, index + 1)} / ${result.iterations_count} pasos`;
  $('iteration-slider').max = Math.max(0, result.iterations.length - 1);
  $('iteration-slider').value = Math.max(0, index);
  $('iteration-slider').disabled = !result.iterations.length;
  $('iteration-slider').setAttribute('aria-valuetext', row ? `Iteración ${row.n} de ${result.iterations_count}` : 'Sin iteraciones');
  $('state').textContent = finished ? result.status : 'Revisando pasos';
  $('state').className = `status ${finished ? (result.converged ? 'status-success' : 'status-warning') : ''}`;

  // Explicación en palabras + fórmula del paso con los valores sustituidos.
  $('explanation').textContent = row?.explanation || result.message;
  $('explanation-formula').textContent = row?.formula || '';
  $('explanation-formula').hidden = !row?.formula;

  const residual = row ? Math.abs(row.fx) : result.residual;
  $('result-summary').textContent =
    `${finished ? result.message : `Iteración ${index + 1}.`} Aproximación: ${format(row?.x ?? result.root)}` +
    ` · Paso |Δx|: ${format(row ? row.error : result.error)} · Residuo: ${format(residual)}` +
    `${row?.error_bound != null ? ` · Cota de error: ${format(row.error_bound)}` : ''}`;

  const steps = result.iterations;
  const positive = r => (Math.abs(r.fx) > 0 ? Math.abs(r.fx) : null);
  const traces = [line(steps.map(r => r.n), steps.map(positive), '|Residuo|')];
  if (row && positive(row) != null) {
    traces.push(points([row.n], [positive(row)], 'Paso seleccionado', { marker: { size: 12, symbol: 'diamond', color: '#196d61' } }));
  }
  $('convergence-plot').classList.toggle('has-results', Boolean(window.Plotly));
  plot($('convergence-plot'), traces, {
    xaxis: { title: 'Iteración', dtick: 1 },
    yaxis: { title: '|Residuo|', type: 'log' },
    uirevision: generation,
  });
  $('previous').disabled = index <= 0;
  $('next').disabled = finished;
  $('auto').disabled = finished;
  if (finished) stop();
}

// ---------------------------------------------------------------------------
// Exportar CSV y enlace compartible
// ---------------------------------------------------------------------------

function exportCsv() {
  if (!result?.iterations.length) return;
  const values = Object.fromEntries(new FormData(form));
  const csv = buildCsv(method, registry[method], values, result, columns[method]);
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `numlearn-${registry[method].slug}-${new Date().toISOString().slice(0, 10)}.csv`;
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(link.href);
}

function shareUrl() {
  const values = Object.fromEntries(new FormData(form));
  return configurationUrl(location.origin + simulatorUrls[method], values, registry[method].parameters);
}

async function copyLink() {
  const url = shareUrl();
  const feedback = $('copy-feedback');
  try {
    await navigator.clipboard.writeText(url);
    feedback.textContent = 'Enlace copiado. Abre el laboratorio con esta configuración.';
  } catch {
    feedback.textContent = url; // sin permiso de portapapeles: se muestra para copiar a mano
  }
}

// ---------------------------------------------------------------------------
// Eventos
// ---------------------------------------------------------------------------

form.addEventListener('submit', async event => {
  event.preventDefault();
  stop();
  if (await calculate()) {
    index = result.iterations.length - 1;
    render();
  }
});

$('next').addEventListener('click', async () => {
  stop();
  if (await calculate()) {
    index = Math.min(index + 1, result.iterations.length - 1);
    render();
  }
});

$('previous').addEventListener('click', () => selectStep(Math.max(0, index - 1)));
$('iteration-slider').addEventListener('input', event => selectStep(Number(event.target.value)));

$('auto').addEventListener('click', async () => {
  if (timer) {
    stop();
    return;
  }
  if (!(await calculate())) return;
  if (index < 0) {
    index = Math.min(0, result.iterations.length - 1);
    render();
  }
  if (index >= result.iterations.length - 1) return;
  $('auto').textContent = 'Pausar';
  timer = setInterval(() => {
    index++;
    render();
  }, 900);
});

form.addEventListener('input', event => {
  if (event.target.tagName === 'INPUT') {
    invalidate();
    previewTimer = setTimeout(() => preview(), 350);
  }
});

form.addEventListener('reset', () => {
  invalidate();
  setTimeout(() => {
    $('copy-feedback').textContent = '';
    configure();
    preview();
  }, 0);
});

$('export-csv').addEventListener('click', exportCsv);
$('copy-link').addEventListener('click', copyLink);

// Ejemplos: [f(x), a, b, x0, g(x) para punto fijo, guía]
const examples = [
  ['x^3 - x - 2', 1, 2, 1.5, '(x + 2)^0.3333333333333333', 'Compara los pasos de Bisección y Newton con tolerancia 10⁻⁶.'],
  ['cos(x) - x', 0, 1, 0.5, 'cos(x)', 'La raíz está entre 0 y 1.'],
  ['exp(-x) - x', 0, 1, 0.5, 'exp(-x)', 'Observa cómo cambia el residuo.'],
  ['x^2 - 4', 1, 3, 3, '(x + 4/x)/2', 'Este intervalo aísla la raíz positiva 2.'],
  ['(x-1)^2*(x+2)', 0.5, 1.5, 1.8, null, 'Raíz doble en 1: toca el eje sin cambiar de signo. Bisección rechaza [0.5,1.5]; Newton ordinario pierde convergencia cuadrática.'],
  ['(x-1)^2*(x+2)', -3, -1.5, -2.5, null, 'La raíz simple −2 sí cruza el eje. Compara con la raíz doble del mismo polinomio.'],
  ['(x-1)^2*(x+2)', 0.5, 1.5, -1, null, 'En x₀=−1, f′(x₀)=0 y f(x₀)=4. Newton no puede construir el siguiente paso.'],
];

$('example').addEventListener('change', event => {
  if (event.target.value === '') return;
  const [expression, a, b, x0, g, tip] = examples[Number(event.target.value)];
  if (method === 'fixed-point' && !g) {
    showError('Para este ejemplo selecciona Newton, Bisección o Raíces múltiples. No se proporciona una transformación g(x).');
    return;
  }
  invalidate();
  form.elements.expression.value = method === 'fixed-point' ? g : expression;
  for (const [key, val] of Object.entries({ a, b, x0, x1: b })) form.elements[key].value = val;
  $('example-guidance').textContent = tip;
  preview();
});

$('range-form').addEventListener('submit', event => {
  event.preventDefault();
  const a = Number($('range-min').value);
  const b = Number($('range-max').value);
  const y0 = $('y-min').value;
  const y1 = $('y-max').value;
  if (!(a < b) || !Number.isFinite(a) || !Number.isFinite(b)) {
    showError('X mínimo debe ser menor que X máximo.');
    return;
  }
  if ((y0 !== '' || y1 !== '') && (y0 === '' || y1 === '' || !Number.isFinite(Number(y0)) || !Number.isFinite(Number(y1)) || Number(y0) >= Number(y1))) {
    showError('Completa ambos límites Y con mínimo menor que máximo, o deja ambos vacíos.');
    return;
  }
  preview({ x: [a, b], y: y0 === '' ? null : [Number(y0), Number(y1)] });
});

// Selector de método (familias cerrada/abierta). Cambiar de método lleva a su URL canónica
// conservando tolerancia, iteraciones y puntos; la expresión solo si ambos métodos usan f(x)
// (en punto fijo el campo es g(x) y no es intercambiable).
$('method-select')?.addEventListener('change', event => {
  const target = event.target.value;
  if (target === method || !simulatorUrls[target]) return;
  const params = new URLSearchParams();
  if (method !== 'fixed-point' && target !== 'fixed-point') params.set('expression', form.elements.expression.value);
  for (const key of ['tolerance', 'max_iterations', 'a', 'b', 'x0', 'x1']) {
    const field = form.elements[key];
    if (field && !field.disabled && field.value !== '') params.set(key, field.value);
  }
  location.assign(`${simulatorUrls[target]}?${params}`);
});

// Parámetros iniciales por URL (enlaces compartidos desde el historial: misma página, otros valores).
const query = new URLSearchParams(location.search);
for (const key of ['expression', 'tolerance', 'max_iterations', 'a', 'b', 'x0', 'x1']) {
  if (query.has(key)) form.elements[key].value = query.get(key);
}

configure();
preview();
