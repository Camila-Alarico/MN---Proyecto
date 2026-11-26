// Unidad 2 · Raíces de polinomios: división sintética, Birge-Vieta y deflación.
import * as N from '../numeric.js';
import {COLORS, curve, dots, FieldError, fmt, line, parseList} from './framework.js';

const SUPER = '⁰¹²³⁴⁵⁶⁷⁸⁹';
const power = k => k === 0 ? '' : k === 1 ? 'x' : `x${String(k).split('').map(d => SUPER[d]).join('')}`;
export function polynomialText(coefficients) {
  const degree = coefficients.length - 1;
  const parts = [];
  coefficients.forEach((c, i) => {
    if (Math.abs(c) < 1e-12) return;
    const k = degree - i, magnitude = Math.abs(c);
    const number = magnitude === 1 && k > 0 ? '' : fmt(magnitude, 5);
    parts.push(`${c < 0 ? (parts.length ? ' − ' : '−') : (parts.length ? ' + ' : '')}${number}${power(k)}`);
  });
  return parts.join('') || '0';
}

export const polyroots = {
  presets: [
    {label: 'Tres raíces reales', values: {coefficients: '1 -6 11 -6', x0: '0.5'}},
    {label: 'Grado 4', values: {coefficients: '1 -2 -13 14 24', x0: '0'}},
    {label: 'Par complejo', values: {coefficients: '1 -1 1 -1', x0: '0'}},
    {label: 'Raíz doble', values: {coefficients: '1 -4 5 -2', x0: '3'}},
  ],
  fields: [
    {name: 'coefficients', label: 'Coeficientes (de mayor a menor grado)', type: 'text', value: '1 -6 11 -6',
     hint: 'Separados por espacios. «1 -6 11 -6» es x³ − 6x² + 11x − 6.'},
    {name: 'x0', label: 'Valor inicial x₀', type: 'number', value: '0.5', half: true},
    {name: 'tolerance', label: 'Tolerancia', type: 'number', value: '1e-8', min: 1e-14, max: 1, half: true},
  ],
  run({coefficients, x0, tolerance}) {
    const list = parseList('coefficients', coefficients, 2);
    if (list[0] === 0) throw new FieldError('coefficients', 'El primer coeficiente (el de mayor grado) no puede ser cero.');
    if (list.length > 9) throw new FieldError('coefficients', 'Usa un polinomio de grado 8 como máximo.');
    const result = N.polynomialRoots(list, x0, tolerance);
    const degree = list.length - 1;
    const roots = result.roots.map(root => ({text: fmt(root, 8), real: root}));
    let leftover = '';
    if (result.remaining.length === 3) {
      const [a, b, c] = result.remaining, real = -b / (2 * a), imaginary = Math.sqrt(4 * a * c - b * b) / (2 * Math.abs(a));
      roots.push({text: `${fmt(real, 6)} + ${fmt(imaginary, 6)}i`}, {text: `${fmt(real, 6)} − ${fmt(imaginary, 6)}i`});
      leftover = `El cociente ${polynomialText(result.remaining)} no tiene raíces reales: se resolvió con la fórmula cuadrática.`;
    } else if (result.remaining.length > 3) {
      leftover = `Quedó sin factorizar ${polynomialText(result.remaining)}: sus raíces son complejas y Newton con valores reales no las alcanza (usa Müller o Bairstow).`;
    }
    const reals = result.roots;
    const center = reals.length ? (Math.min(...reals) + Math.max(...reals)) / 2 : x0;
    const half = Math.max(2, reals.length ? (Math.max(...reals) - Math.min(...reals)) * 0.75 : 3);
    const graph = curve(x => N.polyval(list, x), center - half, center + half);
    const first = result.stages[0];
    const cards = [
      {title: `p(x) = ${polynomialText(list)}`, note: 'Las raíces reales son los cruces con el eje horizontal.',
       plot: {traces: [
         line(graph.x, graph.y, 'p(x)', {line: {color: COLORS[0], width: 2.6}}),
         dots(reals, reals.map(() => 0), 'Raíces reales', {marker: {size: 12, color: '#1f7a48', line: {color: '#fff', width: 2}}}),
         ...(first ? [dots(first.iterations.map(it => it.x), first.iterations.map(it => it.p), 'Iteraciones de Newton', {marker: {size: 8, color: COLORS[1], symbol: 'diamond'}})] : []),
       ]}},
      {title: 'Deflación etapa por etapa', steps: [
        ...result.stages.map((stage, index) => [`Etapa ${index + 1}.`,
          `En ${polynomialText(stage.polynomial)}, desde x₀ = ${fmt(stage.start, 4)}, Newton converge a r = ${fmt(stage.root, 8)} en ${stage.iterations.length} iteraciones. Cociente: ${polynomialText(stage.quotient)}.`]),
        ...(result.remaining.length === 1 && degree > 1 ? [['Última raíz.', 'El cociente final es de grado 1 y se despeja directamente.']] : []),
        ...(leftover ? [['Resto.', leftover]] : []),
      ]},
    ];
    if (first) cards.push({title: 'Birge-Vieta sobre el polinomio original', note: 'Cada fila usa dos divisiones sintéticas: una da p(xᵢ) y la otra p′(xᵢ).',
      table: {columns: ['i', 'xᵢ', 'p(xᵢ)', 'p′(xᵢ)', 'xᵢ₊₁', '|xᵢ₊₁ − xᵢ|'], keyRows: [first.iterations.length - 1],
              rows: first.iterations.map(it => [String(it.n), fmt(it.x, 8), fmt(it.p, 6), fmt(it.dp, 6), fmt(it.next, 8), fmt(it.step, 3)])}});
    const complete = roots.length === degree;
    return {
      status: complete
        ? {kind: leftover ? 'warn' : 'ok', text: leftover || `Se encontraron las ${degree} raíces: ${degree - 1 > 0 ? 'una búsqueda iterativa por etapa y deflación.' : 'ecuación lineal.'}`}
        : {kind: 'warn', text: leftover || 'No se encontraron todas las raíces reales: prueba con otro valor inicial.'},
      metrics: [
        {label: 'Grado', value: String(degree)},
        {label: 'Raíces encontradas', value: `${roots.length} de ${degree}`, tone: complete ? 'good' : 'bad'},
        ...roots.slice(0, 6).map((root, index) => ({label: `r${index + 1}`, value: root.text})),
      ],
      cards,
    };
  },
};
