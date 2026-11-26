// Marco común de los laboratorios del temario: formulario con validación en vivo, estado,
// métricas, gráficas (Plotly), tablas y pasos. Cada laboratorio solo declara sus campos y `run`.
import {chartLayout} from '../../nonlinear/chart-theme.js';
import {compile, ExpressionError} from '../expr.js';
import {NumericError, fmt} from '../numeric.js';

export {fmt};
export const COLORS = ['#5746bb', '#c0562b', '#1f8a70', '#b23a6b', '#2f6fd0', '#8a6d1f'];

/** Error asociado a un campo: el marco lo muestra junto al control. */
export class FieldError extends Error {
  constructor(field, message) { super(message); this.field = field; }
}

export function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (value == null || value === false) continue;
    if (key === 'class') node.className = value;
    else if (key === 'text') node.textContent = value;
    else if (key in node && key !== 'list' && key !== 'form') node[key] = value;
    else node.setAttribute(key, value === true ? '' : value);
  }
  for (const child of children.flat()) if (child != null) node.append(child);
  return node;
}

// --- Lectura de datos escritos por el estudiante ------------------------------------------------
const toNumber = text => {
  const clean = text.trim().replace(/[−–]/g, '-').replace(',', '.');
  return clean === '' || !/^[-+]?(\d+\.?\d*|\.\d+)(e[-+]?\d+)?$/i.test(clean) ? NaN : Number(clean);
};
export function parseFunction(field, text, variables = ['x']) {
  try { return compile(text, variables); }
  catch (error) { throw new FieldError(field, error instanceof ExpressionError ? error.message : 'No se pudo interpretar la expresión.'); }
}
/** Un punto «x, y» por línea (también acepta espacio o punto y coma como separador). */
export function parsePoints(field, text, minimum = 2) {
  const points = [];
  text.split(/\n/).forEach((line, index) => {
    if (!line.trim()) return;
    const parts = line.trim().split(/[;\s]+|,\s+|,(?=[-+\d.])/).filter(Boolean);
    const values = parts.map(toNumber);
    if (parts.length !== 2 || values.some(Number.isNaN)) throw new FieldError(field, `Línea ${index + 1}: escribe dos números, «x, y». Leí «${line.trim()}».`);
    points.push(values);
  });
  if (points.length < minimum) throw new FieldError(field, `Escribe al menos ${minimum} puntos, uno por línea.`);
  if (points.length > 30) throw new FieldError(field, 'Usa como máximo 30 puntos.');
  return points;
}
/** Una fila por línea: coeficientes separados por espacios y, tras «|», el término independiente. */
export function parseSystem(field, text, {needVector = true} = {}) {
  const matrix = [], vector = [];
  text.split(/\n/).forEach((line, index) => {
    if (!line.trim()) return;
    const [left, right] = line.split('|');
    const row = left.trim().split(/[\s,;]+/).filter(Boolean).map(toNumber);
    if (!row.length || row.some(Number.isNaN)) throw new FieldError(field, `Fila ${index + 1}: solo números separados por espacios. Leí «${line.trim()}».`);
    matrix.push(row);
    if (right !== undefined && right.trim()) {
      const value = toNumber(right);
      if (Number.isNaN(value)) throw new FieldError(field, `Fila ${index + 1}: el término independiente «${right.trim()}» no es un número.`);
      vector.push(value);
    } else if (needVector) throw new FieldError(field, `Fila ${index + 1}: falta el término independiente después de «|».`);
  });
  const n = matrix.length;
  if (n < 2 || n > 6) throw new FieldError(field, 'Escribe entre 2 y 6 ecuaciones, una por línea.');
  const bad = matrix.findIndex(row => row.length !== n);
  if (bad >= 0) throw new FieldError(field, `Fila ${bad + 1}: tiene ${matrix[bad].length} coeficientes y deberían ser ${n} (matriz cuadrada).`);
  return {matrix, vector, n};
}
export function parseList(field, text, minimum = 2) {
  const parts = text.trim().split(/[\s,;]+/).filter(Boolean);
  const values = parts.map(toNumber);
  const bad = values.findIndex(Number.isNaN);
  if (bad >= 0) throw new FieldError(field, `«${parts[bad]}» no es un número.`);
  if (values.length < minimum) throw new FieldError(field, `Escribe al menos ${minimum} números separados por espacios.`);
  return values;
}
/** Evalúa una función en una malla y sustituye los valores no finitos por huecos en la gráfica. */
export function curve(f, a, b, count = 240) {
  const x = [], y = [];
  for (let i = 0; i < count; i++) {
    const value = a + (b - a) * i / (count - 1), result = f(value);
    x.push(value);
    y.push(Number.isFinite(result) && Math.abs(result) < 1e12 ? result : null);
  }
  return {x, y};
}
export const line = (x, y, name, extra = {}) => ({x, y, name, type: 'scatter', mode: 'lines', line: {width: 2.4}, ...extra});
export const dots = (x, y, name, extra = {}) => ({x, y, name, type: 'scatter', mode: 'markers', marker: {size: 9}, ...extra});
export const pct = value => value == null || !Number.isFinite(value) ? '—' : `${fmt(value * 100, 4)} %`;
export const matrixRows = (matrix, digits = 6) => matrix.map(row => row.map(value => fmt(value, digits)));

// --- Montaje ---------------------------------------------------------------------------------------
const STATUS_ICONS = {ok: 'bi-check-circle-fill', warn: 'bi-exclamation-triangle-fill', bad: 'bi-x-octagon-fill', info: 'bi-info-circle-fill'};
let serial = 0;

export function mountLab(container, definition) {
  const id = `lab-${++serial}`;
  const controls = new Map();
  const form = el('form', {class: 'lab-controls', novalidate: true, 'aria-label': 'Datos del laboratorio'});
  form.append(el('h3', {text: 'Datos'}));

  let presetButtons = [];
  if (definition.presets?.length) {
    const group = el('div', {class: 'lab-presets', role: 'group', 'aria-label': 'Ejemplos'});
    presetButtons = definition.presets.map((preset, index) => {
      const button = el('button', {type: 'button', class: 'lab-preset', text: preset.label, 'aria-pressed': index === 0 ? 'true' : 'false'});
      button.addEventListener('click', () => { applyPreset(index); schedule(0); });
      group.append(button);
      return button;
    });
    form.append(group);
  }

  let row = null;
  for (const field of definition.fields) {
    const fieldId = `${id}-${field.name}`;
    const wrapper = el('div', {class: 'lab-field', 'data-field': field.name});
    const label = el('label', {for: fieldId}, el('span', {text: field.label}));
    let input, output;
    if (field.type === 'select') {
      input = el('select', {id: fieldId}, field.options.map(([value, text]) => el('option', {value, text})));
    } else if (field.type === 'textarea') {
      input = el('textarea', {id: fieldId, rows: field.rows || 5, spellcheck: false});
    } else if (field.type === 'range') {
      input = el('input', {id: fieldId, type: 'range', min: field.min, max: field.max, step: field.step || 1});
      output = el('output', {for: fieldId});
      label.append(output);
    } else if (field.type === 'checks') {
      input = el('div', {class: 'lab-checks', id: fieldId, role: 'group', 'aria-label': field.label});
      field.options.forEach(([value, text, color]) => input.append(el('label', {},
        el('input', {type: 'checkbox', value}), color ? el('span', {class: 'lab-swatch', style: `background:${color}`}) : null, el('span', {text}))));
    } else {
      input = el('input', {id: fieldId, type: 'text', inputMode: field.type === 'number' ? 'decimal' : 'text', autocomplete: 'off', spellcheck: false});
    }
    const error = el('p', {class: 'lab-error', id: `${fieldId}-error`, hidden: true});
    if (field.type !== 'checks') input.setAttribute('aria-describedby', error.id);
    wrapper.append(field.type === 'checks' ? el('label', {}, el('span', {text: field.label})) : label, input);
    if (field.hint) wrapper.append(el('p', {class: 'lab-hint', text: field.hint}));
    wrapper.append(error);
    controls.set(field.name, {field, wrapper, input, output, error});
    if (field.half) {
      if (!row) { row = el('div', {class: 'lab-row'}); form.append(row); }
      row.append(wrapper);
      if (row.children.length === 2) row = null;
    } else { row = null; form.append(wrapper); }
  }
  const reset = el('button', {type: 'button', class: 'btn btn-light', text: '↺ Restablecer'});
  form.append(el('div', {class: 'lab-actions'}, reset));

  const statusText = el('span', {text: 'Preparando…'});
  const statusIcon = el('i', {class: 'bi bi-info-circle-fill', 'aria-hidden': 'true'});
  const live = el('span', {class: 'lab-live'});
  const status = el('div', {class: 'lab-status is-info', role: 'status', 'aria-live': 'polite', 'data-testid': 'lab-status'}, statusIcon, statusText, live);
  const metrics = el('div', {class: 'lab-metrics', 'data-testid': 'lab-metrics'});
  const cards = el('div', {class: 'lab-output'});
  const output = el('div', {class: 'lab-output'}, status, metrics, cards);
  container.replaceChildren(form, output);

  function setValue(name, value) {
    const control = controls.get(name);
    if (!control) return;
    if (control.field.type === 'checks') control.input.querySelectorAll('input').forEach(box => { box.checked = value.includes(box.value); });
    else control.input.value = value;
    syncOutput(control);
  }
  function syncOutput(control) {
    if (control.output) control.output.textContent = control.field.format ? control.field.format(Number(control.input.value)) : control.input.value;
  }
  function applyPreset(index) {
    definition.fields.forEach(field => setValue(field.name, field.value));
    const preset = definition.presets?.[index];
    if (preset) Object.entries(preset.values).forEach(([name, value]) => setValue(name, value));
    presetButtons.forEach((button, i) => button.setAttribute('aria-pressed', String(i === index)));
  }
  function setError(name, message) {
    const control = controls.get(name);
    if (!control) return;
    control.wrapper.classList.toggle('is-invalid', Boolean(message));
    control.wrapper.classList.toggle('is-valid', !message);
    control.error.hidden = !message;
    control.error.replaceChildren(...(message ? [el('i', {class: 'bi bi-exclamation-circle', 'aria-hidden': 'true'}), el('span', {text: message})] : []));
    if (control.field.type !== 'checks') control.input.setAttribute('aria-invalid', String(Boolean(message)));
  }

  function readValues() {
    const values = {};
    let failed = false;
    for (const [name, {field, input}] of controls) {
      setError(name, '');
      if (field.type === 'checks') { values[name] = [...input.querySelectorAll('input:checked')].map(box => box.value); continue; }
      if (field.type === 'number' || field.type === 'range') {
        const number = toNumber(input.value);
        let message = '';
        if (Number.isNaN(number)) message = input.value.trim() ? 'Escribe un número (por ejemplo 0.5 o 1e-3).' : 'Este dato es obligatorio.';
        else if (field.integer && !Number.isInteger(number)) message = 'Debe ser un número entero.';
        else if (field.min != null && number < field.min) message = `El valor mínimo es ${field.min}.`;
        else if (field.max != null && number > field.max) message = `El valor máximo es ${field.max}.`;
        if (message) { setError(name, message); failed = true; }
        values[name] = number;
      } else {
        values[name] = input.value;
        if (field.type !== 'select' && !input.value.trim()) { setError(name, 'Este dato es obligatorio.'); failed = true; }
      }
    }
    return failed ? null : values;
  }
  function setStatus(kind, text) {
    status.className = `lab-status is-${kind}`;
    statusIcon.className = `bi ${STATUS_ICONS[kind]}`;
    statusText.textContent = text;
  }

  let previousMetrics = new Map(), plotNodes = [];
  function render(result) {
    setStatus(result.status?.kind || 'ok', result.status?.text || 'Cálculo actualizado.');
    const nextMetrics = new Map();
    metrics.replaceChildren(...(result.metrics || []).map(metric => {
      const node = el('div', {class: `lab-metric${metric.tone ? ` is-${metric.tone}` : ''}`},
        el('span', {text: metric.label}), el('strong', {text: metric.value}), metric.hint ? el('small', {text: metric.hint}) : null);
      nextMetrics.set(metric.label, metric.value);
      if (previousMetrics.has(metric.label) && previousMetrics.get(metric.label) !== metric.value) node.classList.add('is-changed');
      return node;
    }));
    previousMetrics = nextMetrics;
    const plots = [];
    const nodes = (result.cards || []).map((card, index) => {
      const node = el('section', {class: 'lab-card'});
      if (card.title) node.append(el('h3', {text: card.title}));
      if (card.note) node.append(el('p', {text: card.note}));
      if (card.plot) {
        // Se reutiliza el nodo de la gráfica para que Plotly anime el cambio en vez de redibujar todo.
        const target = plotNodes[index] || el('div', {class: 'lab-plot', role: 'img'});
        target.classList.toggle('is-small', Boolean(card.plot.small));
        target.setAttribute('aria-label', card.plot.label || card.title || 'Gráfica del laboratorio');
        plotNodes[index] = target;
        plots.push([target, card.plot]);
        node.append(target);
      }
      for (const item of card.matrices || []) {
        const columns = item.data[0].length;
        const grid = el('span', {class: 'lab-matrix', style: `grid-template-columns:repeat(${columns},auto)`});
        item.data.forEach(row => row.forEach((value, j) => grid.append(el('span', {class: item.sep != null && j === item.sep ? 'is-sep' : null, text: fmt(value, 6)}))));
        node.append(el('div', {class: 'lab-matrix-item'}, el('span', {class: 'lab-matrix-label', text: item.label}), grid));
      }
      if (card.steps) node.append(el('ol', {class: 'lab-steps'}, card.steps.map(step => Array.isArray(step) ? el('li', {}, el('b', {text: `${step[0]} `}), step[1]) : el('li', {text: step}))));
      if (card.table) {
        const table = el('table', {class: 'table lab-table'});
        if (card.table.caption) table.createCaption().textContent = card.table.caption;
        const head = table.createTHead().insertRow();
        card.table.columns.forEach(text => head.append(el('th', {scope: 'col', text})));
        const body = table.createTBody();
        card.table.rows.forEach((cells, r) => {
          const tr = body.insertRow();
          if (card.table.keyRows?.includes(r)) tr.className = 'is-key';
          cells.forEach((text, c) => { const td = tr.insertCell(); td.textContent = text; if (card.table.keyCells?.some(([kr, kc]) => kr === r && kc === c)) td.className = 'is-key'; });
        });
        node.append(el('div', {class: 'table-scroll'}, table));
      }
      return node;
    });
    cards.replaceChildren(...nodes);
    plots.forEach(([target, plot]) => {
      if (!window.Plotly) { target.textContent = 'No se pudo cargar la biblioteca de gráficas; las tablas y resultados siguen disponibles.'; return; }
      window.Plotly.react(target, plot.traces, chartLayout({margin: {l: 62, r: 20, t: 54, b: 52}, ...plot.layout}),
        {responsive: true, displaylogo: false, modeBarButtonsToRemove: ['lasso2d', 'select2d']});
    });
  }

  let timer;
  function run() {
    const values = readValues();
    if (!values) { setStatus('bad', 'Revisa los datos marcados en rojo para calcular.'); live.textContent = ''; return; }
    try {
      render(definition.run(values));
      live.replaceChildren(el('i', {class: 'bi bi-check2', 'aria-hidden': 'true'}), 'Actualizado');
    } catch (error) {
      live.textContent = '';
      if (error instanceof FieldError) { setError(error.field, error.message); setStatus('bad', 'Revisa los datos marcados en rojo para calcular.'); }
      else if (error instanceof NumericError || error instanceof ExpressionError) setStatus('bad', error.message);
      else { console.error(error); setStatus('bad', 'No se pudo completar el cálculo con estos datos.'); }
    }
  }
  function schedule(delay = 260) {
    clearTimeout(timer);
    live.replaceChildren(el('span', {class: 'spinner', 'aria-hidden': 'true'}), 'Calculando…');
    timer = setTimeout(run, delay);
  }
  form.addEventListener('input', event => {
    const control = [...controls.values()].find(item => item.input === event.target);
    if (control) syncOutput(control);
    presetButtons.forEach(button => button.setAttribute('aria-pressed', 'false'));
    schedule(event.target.type === 'range' || event.target.type === 'checkbox' ? 30 : 260);
  });
  form.addEventListener('submit', event => { event.preventDefault(); schedule(0); });
  reset.addEventListener('click', () => { applyPreset(0); schedule(0); window.NumLearnFeedback?.toast('Datos restablecidos al ejemplo inicial.', 'info', 2200); });
  applyPreset(0);
  run();
  return {run, setValue};
}
