import {post, plot, line, points, format, showError, busy, setMath, simulatorUrls} from './common.js';

const $ = id => document.getElementById(id);
const form = $('graph-form');
const button = form.querySelector('button[type=submit]');
const target = $('search-plot');
const examples = {
  cubic: {expression: 'x^3-x-2', a: -2, b: 3},
  double: {expression: 'x^2', a: -1, b: 1},
  pole: {expression: '1/x', a: -1, b: 1},
};
let version = 0, controller = null, drawing = Promise.resolve();

function clearPlot(message) {
  if (window.Plotly && target.data) window.Plotly.purge(target);
  target.textContent = message;
}
function invalidate() {
  version++;
  controller?.abort();
  busy(button, false);
  showError('');
  $('graph-state').textContent = 'Datos modificados';
  $('graph-message').textContent = 'Vuelve a explorar para calcular con estos datos.';
  $('graph-candidates').replaceChildren();
  $('graph-results').hidden = true;
  setMath($('graph-formula'), null, 'La fórmula aparecerá al explorar.');
  clearPlot('Confirma la función y el intervalo.');
}
function results(data, values) {
  const zeros = data.sampled_zeros;
  $('graph-zero-count').textContent = zeros.length;
  $('graph-interval-count').textContent = data.intervals.length;
  $('graph-sample-count').textContent = data.x.length;
  $('graph-zero-values').textContent = zeros.length
    ? `Puntos con valor cero: ${zeros.slice(0, 8).map(format).join(', ')}${zeros.length > 8 ? ` y ${zeros.length - 8} más` : ''}.`
    : 'No se encontró valor cero en los puntos evaluados; pueden existir raíces entre ellos.';
  $('graph-zero-values').textContent += ' Se usa la precisión disponible: el muestreo no demuestra que sean todas las raíces.';
  for (const [a, b] of data.intervals) {
    const item = document.createElement('li');
    const link = document.createElement('a');
    link.href = simulatorUrls.bisection + '?' + new URLSearchParams({
      expression: values.expression, a, b, tolerance: '0.000001',
    });
    link.textContent = `Probar [${format(a)}, ${format(b)}] en Bisección →`;
    item.append(link);
    $('graph-candidates').append(item);
  }
  const invalid = data.y.filter(value => value === null).length;
  $('graph-message').textContent = `${invalid ? `${invalid} ${invalid === 1 ? 'punto' : 'puntos'} sin un valor real finito. ` : ''}${data.warning}`;
  $('graph-results').hidden = false;
}
async function calculate() {
  invalidate();
  if (!form.reportValidity()) return;
  const seq = version;
  const values = Object.fromEntries(new FormData(form));
  controller = new AbortController();
  $('graph-state').textContent = 'Explorando…';
  $('graph-message').textContent = 'Evaluando la función en el intervalo indicado.';
  busy(button, true, 'Explorando…');
  try {
    const data = await post('/api/nonlinear/graph/', values, controller.signal);
    if (seq !== version) return;
    const render = async () => {
      if (seq !== version) return;
      const traces = [line(data.x, data.y, 'f(x)')];
      if (data.sampled_zeros.length) traces.push(points(data.sampled_zeros, data.sampled_zeros.map(() => 0), 'Valor cero muestreado', {marker: {symbol: 'diamond-open', size: 12, color: '#92622a'}}));
      await plot(target, traces, {xaxis: {title: 'x', range: [Number(values.a), Number(values.b)], zeroline: true}});
      if (seq !== version) clearPlot('Confirma la función y el intervalo.');
    };
    drawing = drawing.then(render, render);
    await drawing;
    if (seq !== version) return;
    setMath($('graph-formula'), String.raw`f(x)=${data.formula}`, `f(x) = ${values.expression}`);
    results(data, values);
    $('graph-state').textContent = 'Exploración actualizada';
  } catch (error) {
    if (seq !== version || error.name === 'AbortError') return;
    showError(error.message);
    $('graph-state').textContent = 'Revisa los datos';
    $('graph-message').textContent = 'No se obtuvieron resultados para esta configuración.';
  } finally {
    if (seq === version) busy(button, false);
  }
}
form.addEventListener('input', () => {
  $('graph-example').value = 'custom';
  invalidate();
});
form.addEventListener('submit', event => {event.preventDefault(); calculate();});
$('graph-example').addEventListener('change', event => {
  const example = examples[event.target.value];
  if (!example) return;
  for (const [key, value] of Object.entries(example)) form.elements[key].value = value;
  calculate();
});
calculate();
