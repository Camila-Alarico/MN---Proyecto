// Unidad 4 · Ajuste de curvas: regresión, interpolación de Newton, Lagrange y splines, Fourier.
import * as N from '../numeric.js';
import {COLORS, curve, dots, FieldError, fmt, line, parsePoints} from './framework.js';

const POINTS_HINT = 'Un punto por línea: «x, y».';
const xs = points => points.map(point => point[0]);
const ys = points => points.map(point => point[1]);
function range(points, margin = 0.08) {
  const low = Math.min(...xs(points)), high = Math.max(...xs(points)), pad = (high - low || 1) * margin;
  return [low - pad, high + pad];
}

export const regression = {
  presets: [
    {label: 'Siete mediciones', values: {points: '1, 0.5\n2, 2.5\n3, 2.0\n4, 4.0\n5, 3.5\n6, 6.0\n7, 5.5', model: 'linear'}},
    {label: 'Datos curvos', values: {points: '0, 2.1\n1, 7.7\n2, 13.6\n3, 27.2\n4, 40.9\n5, 61.1', model: 'quadratic'}},
    {label: 'Crecimiento', values: {points: '1, 0.5\n2, 1.7\n3, 3.4\n4, 5.7\n5, 8.4', model: 'power'}},
  ],
  fields: [
    {name: 'points', label: 'Datos', type: 'textarea', rows: 7, value: '1, 0.5\n2, 2.5\n3, 2.0\n4, 4.0\n5, 3.5\n6, 6.0\n7, 5.5', hint: POINTS_HINT},
    {name: 'model', label: 'Modelo', type: 'select', value: 'linear', options: [['linear', 'Recta: y = a₀ + a₁x'], ['quadratic', 'Parábola: y = a₀ + a₁x + a₂x²'],
      ['cubic', 'Cúbica'], ['exponential', 'Exponencial: y = α·e^(βx)'], ['power', 'Potencia: y = α·x^β']]},
  ],
  run({points, model}) {
    const data = parsePoints('points', points);
    const degree = {linear: 1, quadratic: 2, cubic: 3}[model];
    if (degree && data.length <= degree) throw new FieldError('points', `Para este modelo hacen falta al menos ${degree + 1} puntos.`);
    const fit = degree ? N.polynomialFit(data, degree) : N.transformedFit(data, model);
    const c = fit.coefficients.map(value => fmt(value, 6));
    const equation = degree ? `y = ${c.map((value, k) => k === 0 ? value : `${value}·x${k > 1 ? '^' + k : ''}`).join(' + ').replace(/\+ −/g, '− ')}`
      : model === 'power' ? `y = ${c[0]}·x^${c[1]}` : `y = ${c[0]}·e^(${c[1]}·x)`;
    const [from, to] = range(data);
    const graph = curve(fit.predict, model === 'power' ? Math.max(from, 1e-6) : from, to);
    const residualX = [], residualY = [];
    data.forEach(([x, y]) => { residualX.push(x, x, null); residualY.push(y, fit.predict(x), null); });
    const good = fit.r2 >= 0.9;
    return {
      status: {kind: good ? 'ok' : fit.r2 >= 0.7 ? 'warn' : 'bad',
               text: `${equation}. El modelo explica el ${fmt(fit.r2 * 100, 4)} % de la variación de los datos${good ? '.' : ': prueba otro modelo o revisa los datos.'}`},
      metrics: [
        {label: 'r² (determinación)', value: fmt(fit.r2, 6), tone: good ? 'good' : 'bad'},
        {label: 'Error estándar', value: fmt(fit.standardError, 6), hint: 'Dispersión típica alrededor de la curva'},
        {label: 'Sᵣ (residuos²)', value: fmt(fit.sr, 6)}, {label: 'Sₜ (total)', value: fmt(fit.st, 6)},
      ],
      cards: [
        {title: 'Datos y curva ajustada', note: 'Los segmentos verticales son los residuos: el método minimiza la suma de sus cuadrados.',
         plot: {traces: [
           line(residualX, residualY, 'Residuos', {line: {color: '#c9485b', width: 1.6, dash: 'dot'}}),
           line(graph.x, graph.y, 'Ajuste', {line: {color: COLORS[0], width: 2.8}}),
           dots(xs(data), ys(data), 'Datos', {marker: {size: 10, color: COLORS[1], line: {color: '#fff', width: 1.5}}}),
         ]}},
        {title: 'Residuos punto por punto', table: {columns: ['xᵢ', 'yᵢ', 'ŷᵢ (modelo)', 'Residuo yᵢ − ŷᵢ'],
          rows: data.map(([x, y]) => [fmt(x), fmt(y), fmt(fit.predict(x), 7), fmt(y - fit.predict(x), 6)])}},
      ],
    };
  },
};

export const newtoninterp = {
  presets: [
    {label: 'ln x con 4 puntos', values: {points: '1, 0\n4, 1.386294\n6, 1.791759\n5, 1.609438', x: '2'}},
    {label: 'Paso constante', values: {points: '0, 1\n0.5, 1.648721\n1, 2.718282\n1.5, 4.481689\n2, 7.389056', x: '0.75'}},
    {label: 'Dos puntos (lineal)', values: {points: '1, 0\n6, 1.791759', x: '2'}},
  ],
  fields: [
    {name: 'points', label: 'Puntos (xᵢ, yᵢ)', type: 'textarea', rows: 5, value: '1, 0\n4, 1.386294\n6, 1.791759\n5, 1.609438', hint: POINTS_HINT + ' El orden define x₀, x₁, …'},
    {name: 'x', label: 'Interpolar en x', type: 'number', value: '2'},
  ],
  run({points, x}) {
    const data = parsePoints('points', points);
    if (data.length > 8) throw new FieldError('points', 'Usa como máximo 8 puntos: con más, el polinomio oscila demasiado.');
    const result = N.dividedDifferences(data);
    const value = result.evaluate(x);
    const n = data.length;
    const [low, high] = [Math.min(...xs(data)), Math.max(...xs(data))];
    const inside = x >= low && x <= high;
    const [from, to] = range([...data, [x, 0]]);
    const graph = curve(result.evaluate, from, to);
    const partial = result.coefficients.map((_, order) => order ? N.dividedDifferences(data.slice(0, order + 1)).evaluate(x) : data[0][1]);
    const finite = N.forwardDifferences(data);
    const rows = data.map(([xi], i) => [fmt(xi), ...result.table.map(column => i < column.length ? fmt(column[i], 7) : '')]);
    const cards = [
      {title: 'Polinomio interpolante', note: 'Pasa exactamente por todos los puntos.',
       plot: {traces: [
         line(graph.x, graph.y, `Polinomio de grado ${n - 1}`, {line: {color: COLORS[0], width: 2.6}}),
         dots(xs(data), ys(data), 'Puntos dados', {marker: {size: 10, color: COLORS[1], line: {color: '#fff', width: 1.5}}}),
         dots([x], [value], 'Valor interpolado', {marker: {size: 13, color: '#1f7a48', symbol: 'diamond'}}),
       ]}},
      {title: 'Tabla de diferencias divididas', note: 'La primera fila (resaltada) contiene los coeficientes b₀, b₁, … del polinomio de Newton.',
       table: {columns: ['xᵢ', 'f(xᵢ)', ...result.table.slice(1).map((_, k) => `Orden ${k + 1}`)], rows,
               keyCells: result.table.map((_, k) => [0, k + 1])}},
      {title: 'Cómo mejora al añadir términos', table: {columns: ['Grado', 'Coeficiente bₖ', `pₖ(${fmt(x)})`, 'Cambio'],
        rows: partial.map((estimate, k) => [String(k), fmt(result.coefficients[k], 7), fmt(estimate, 8), k ? fmt(Math.abs(estimate - partial[k - 1]), 3) : '—']), keyRows: [n - 1]}},
    ];
    if (finite.uniform && n > 2) cards.push({title: 'Diferencias finitas hacia adelante', note: `Los datos tienen paso constante h = ${fmt(finite.h)}: f[x₀,…,xₖ] = Δᵏf₀ / (k!·hᵏ).`,
      table: {columns: ['xᵢ', 'fᵢ', ...finite.table.slice(1).map((_, k) => `Δ${k ? '^' + (k + 1) : ''}f`)],
              rows: data.map(([xi], i) => [fmt(xi), ...finite.table.map(column => i < column.length ? fmt(column[i], 7) : '')])}});
    return {
      status: inside ? {kind: 'ok', text: `p(${fmt(x)}) = ${fmt(value, 8)} con un polinomio de grado ${n - 1}. El último término aportó ${n > 1 ? fmt(Math.abs(value - partial[n - 2]), 3) : '—'}: sirve como estimación del error.`}
        : {kind: 'warn', text: `x = ${fmt(x)} está fuera del intervalo de los datos [${fmt(low)}, ${fmt(high)}]: esto es extrapolar y el resultado es poco fiable.`},
      metrics: [{label: `p(${fmt(x)})`, value: fmt(value, 8), tone: inside ? 'good' : 'bad'}, {label: 'Grado', value: String(n - 1)},
                {label: 'Aporte del último término', value: n > 1 ? fmt(Math.abs(value - partial[n - 2]), 3) : '—', hint: 'Estimación del error'}],
      cards,
    };
  },
};

const RUNGE = Array.from({length: 9}, (_, i) => { const x = -1 + i / 4; return `${x}, ${(1 / (1 + 25 * x * x)).toFixed(6)}`; }).join('\n');
export const splines = {
  presets: [
    {label: 'Cuatro puntos', values: {points: '3, 2.5\n4.5, 1\n7, 2.5\n9, 0.5', x: '5'}},
    {label: 'ln x (Lagrange)', values: {points: '1, 0\n4, 1.386294\n6, 1.791759', x: '2'}},
    {label: 'Fenómeno de Runge', values: {points: RUNGE, x: '0.9'}},
  ],
  fields: [
    {name: 'points', label: 'Puntos (xᵢ, yᵢ)', type: 'textarea', rows: 6, value: '3, 2.5\n4.5, 1\n7, 2.5\n9, 0.5', hint: POINTS_HINT},
    {name: 'x', label: 'Evaluar en x', type: 'number', value: '5'},
    {name: 'show', label: 'Curvas', type: 'checks', value: ['lagrange', 'cubic', 'linear'],
     options: [['lagrange', 'Polinomio de Lagrange', COLORS[1]], ['cubic', 'Spline cúbico natural', COLORS[0]], ['linear', 'Spline lineal', COLORS[2]]]},
  ],
  run({points, x, show}) {
    const data = parsePoints('points', points);
    if (data.length > 15) throw new FieldError('points', 'Usa como máximo 15 puntos.');
    const spline = N.naturalSpline(data), linear = N.linearSpline(data);
    const lagrange = N.lagrange(data, x);
    const low = spline.points[0][0], high = spline.points[spline.points.length - 1][0];
    if (x < low || x > high) throw new FieldError('x', `Elige x dentro del intervalo de los datos [${fmt(low)}, ${fmt(high)}].`);
    const graphs = {lagrange: curve(v => N.lagrange(data, v).value, low, high, 300), cubic: curve(spline.evaluate, low, high, 300), linear: curve(linear, low, high, 300)};
    const names = {lagrange: `Lagrange (grado ${data.length - 1})`, cubic: 'Spline cúbico natural', linear: 'Spline lineal'};
    const colors = {lagrange: COLORS[1], cubic: COLORS[0], linear: COLORS[2]};
    const dataLow = Math.min(...ys(data)), dataHigh = Math.max(...ys(data)), spanY = dataHigh - dataLow || 1;
    const wild = Math.max(...graphs.lagrange.y.map(v => v ?? 0)) > dataHigh + spanY * 0.5 || Math.min(...graphs.lagrange.y.map(v => v ?? 0)) < dataLow - spanY * 0.5;
    const values = {lagrange: lagrange.value, cubic: spline.evaluate(x), linear: linear(x)};
    return {
      status: wild ? {kind: 'warn', text: 'El polinomio de Lagrange oscila mucho más allá de los datos (fenómeno de Runge). El spline cúbico se mantiene cerca de los puntos.'}
        : {kind: 'ok', text: `En x = ${fmt(x)}: Lagrange da ${fmt(values.lagrange, 7)} y el spline cúbico ${fmt(values.cubic, 7)}. Los pesos de Lagrange suman ${fmt(lagrange.basis.reduce((s, v) => s + v, 0), 6)}.`},
      metrics: [{label: 'Lagrange', value: fmt(values.lagrange, 7)}, {label: 'Spline cúbico', value: fmt(values.cubic, 7), tone: 'good'},
                {label: 'Spline lineal', value: fmt(values.linear, 7)}],
      cards: [
        {title: 'Un polinomio frente a tramos suaves', note: 'Activa o desactiva las curvas para compararlas.',
         plot: {traces: [
           ...['linear', 'lagrange', 'cubic'].filter(key => show.includes(key)).map(key => line(graphs[key].x, graphs[key].y, names[key], {line: {color: colors[key], width: key === 'cubic' ? 2.8 : 2, dash: key === 'lagrange' ? 'dash' : 'solid'}})),
           dots(xs(data), ys(data), 'Puntos', {marker: {size: 10, color: '#172544', line: {color: '#fff', width: 1.5}}}),
           dots([x], [values.cubic], 'Spline en x', {marker: {size: 12, color: '#1f7a48', symbol: 'diamond'}}),
         ], layout: {yaxis: {range: [dataLow - spanY * 0.6, dataHigh + spanY * 0.6], title: 'y'}}}},
        {title: 'Pesos de Lagrange en x', note: 'Cada Lᵢ(x) pondera su yᵢ. Valen 1 en su nodo y 0 en los demás.',
         table: {columns: ['i', 'xᵢ', 'yᵢ', `Lᵢ(${fmt(x)})`, 'Lᵢ·yᵢ'], rows: data.map(([xi, yi], i) => [String(i), fmt(xi), fmt(yi), fmt(lagrange.basis[i], 6), fmt(lagrange.basis[i] * yi, 6)])}},
        {title: 'Tramos del spline cúbico', note: 'sᵢ(x) = aᵢ + bᵢ(x − xᵢ) + cᵢ(x − xᵢ)² + dᵢ(x − xᵢ)³. El tramo que contiene a x está resaltado.',
         table: {columns: ['Tramo', 'aᵢ', 'bᵢ', 'cᵢ', 'dᵢ'], keyRows: [Math.max(0, spline.segments.findIndex(s => x <= s.x1))],
                 rows: spline.segments.map(s => [`[${fmt(s.x0)}, ${fmt(s.x1)}]`, fmt(s.a, 6), fmt(s.b, 6), fmt(s.c, 6), fmt(s.d, 6)])}},
      ],
    };
  },
};

export const fourier = {
  presets: [{label: 'Onda cuadrada', values: {wave: 'square', harmonics: 5}}, {label: 'Diente de sierra', values: {wave: 'sawtooth', harmonics: 8}},
            {label: 'Triangular', values: {wave: 'triangle', harmonics: 3}}, {label: 'Seno rectificado', values: {wave: 'rectified', harmonics: 4}}],
  fields: [
    {name: 'wave', label: 'Señal periódica (T = 2π)', type: 'select', value: 'square', options: Object.entries(N.WAVES).map(([key, item]) => [key, item.label])},
    {name: 'harmonics', label: 'Número de armónicos N', type: 'range', min: 1, max: 40, step: 1, value: 5, hint: 'Desliza para ver cómo la suma se acerca a la señal.'},
  ],
  run({wave, harmonics}) {
    const f = N.WAVES[wave].f;
    const result = N.fourierCoefficients(f, harmonics);
    const t = N.linspace(-2 * Math.PI, 2 * Math.PI, 721);
    const amplitude = result.a.map((a, i) => Math.hypot(a, result.b[i]));
    const overshoot = Math.max(...t.map(result.series)) - Math.max(...t.map(f));
    const jump = wave === 'square' || wave === 'sawtooth';
    const good = result.rms < 0.05;
    return {
      status: {kind: good ? 'ok' : 'warn', text: jump
        ? `Con ${harmonics} armónicos el error cuadrático medio es ${fmt(result.rms, 4)}. Cerca del salto queda un sobrepico de ${fmt(overshoot, 3)} que no desaparece: fenómeno de Gibbs.`
        : `Con ${harmonics} armónicos el error cuadrático medio es ${fmt(result.rms, 4)}. Esta señal es continua: la serie converge rápido.`},
      metrics: [{label: 'Error cuadrático medio', value: fmt(result.rms, 4), tone: good ? 'good' : null}, {label: 'Valor medio a₀', value: fmt(result.a0, 6)},
                {label: 'Armónico dominante', value: `k = ${amplitude.indexOf(Math.max(...amplitude)) + 1}`, hint: `Amplitud ${fmt(Math.max(...amplitude), 5)}`},
                {label: 'Sobrepico', value: fmt(Math.max(0, overshoot), 3)}],
      cards: [
        {title: 'Señal y suma parcial de Fourier', plot: {traces: [
          line(t, t.map(f), N.WAVES[wave].label, {line: {color: '#9aa5bb', width: 2, shape: 'linear'}}),
          line(t, t.map(result.series), `Suma con ${harmonics} armónicos`, {line: {color: COLORS[0], width: 2.6}}),
        ], layout: {xaxis: {title: 't'}, yaxis: {title: 'f(t)'}}}},
        {title: 'Espectro de amplitudes', note: 'Altura de cada barra: amplitud del armónico k, √(aₖ² + bₖ²).',
         plot: {small: true, traces: [{type: 'bar', x: amplitude.map((_, i) => i + 1), y: amplitude, name: 'Amplitud', marker: {color: COLORS[0]}}],
                layout: {xaxis: {title: 'Armónico k', dtick: harmonics > 20 ? 5 : 1}, yaxis: {title: 'Amplitud'}, showlegend: false}}},
        {title: 'Coeficientes', table: {columns: ['k', 'aₖ (coseno)', 'bₖ (seno)', 'Amplitud'],
          rows: amplitude.slice(0, 12).map((value, i) => [String(i + 1), fmt(result.a[i], 6), fmt(result.b[i], 6), fmt(value, 6)])}},
      ],
    };
  },
};
