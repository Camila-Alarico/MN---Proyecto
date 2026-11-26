// Unidad 5 · Integración (trapecio, Simpson, Romberg, integral doble) y derivación numérica.
import * as N from '../numeric.js';
import {COLORS, curve, dots, FieldError, fmt, line, parseFunction, pct} from './framework.js';

const FUNCTION_HINT = 'Usa x, + − * / ^, sin, cos, tan, exp, ln, sqrt, abs, pi, e.';
const RULES = {trapezoid: {label: 'Trapecio compuesto', order: 2, run: N.trapezoid}, simpson13: {label: 'Simpson 1/3 compuesto', order: 4, run: N.simpson13},
               simpson38: {label: 'Simpson 3/8 compuesto', order: 4, run: N.simpson38}};

export const integration = {
  presets: [
    {label: 'Polinomio de grado 5', values: {expression: '0.2 + 25x - 200x^2 + 675x^3 - 900x^4 + 400x^5', a: '0', b: '0.8', n: 4, rule: 'trapezoid'}},
    {label: 'sen(x) en [0, π]', values: {expression: 'sin(x)', a: '0', b: 'pi', n: 6, rule: 'simpson13'}},
    {label: 'Campana e^(−x²)', values: {expression: 'exp(-x^2)', a: '-2', b: '2', n: 12, rule: 'simpson38'}},
  ],
  fields: [
    {name: 'expression', label: 'Función f(x)', type: 'text', value: '0.2 + 25x - 200x^2 + 675x^3 - 900x^4 + 400x^5', hint: FUNCTION_HINT},
    {name: 'a', label: 'Límite inferior a', type: 'text', value: '0', half: true},
    {name: 'b', label: 'Límite superior b', type: 'text', value: '0.8', half: true},
    {name: 'rule', label: 'Regla', type: 'select', value: 'trapezoid', options: Object.entries(RULES).map(([key, rule]) => [key, rule.label])},
    {name: 'n', label: 'Subintervalos n', type: 'range', min: 1, max: 48, step: 1, value: 4},
  ],
  run({expression, a, b, rule, n}) {
    const f = parseFunction('expression', expression);
    const lower = parseFunction('a', a, [])(), upper = parseFunction('b', b, [])();
    if (!Number.isFinite(lower)) throw new FieldError('a', 'El límite debe ser un número (puedes usar pi o e).');
    if (!Number.isFinite(upper)) throw new FieldError('b', 'El límite debe ser un número (puedes usar pi o e).');
    if (upper <= lower) throw new FieldError('b', 'El límite superior debe ser mayor que el inferior.');
    if (rule === 'simpson13' && n % 2) throw new FieldError('n', `Simpson 1/3 necesita n par: prueba ${n + 1}.`);
    if (rule === 'simpson38' && n % 3) throw new FieldError('n', `Simpson 3/8 necesita n múltiplo de 3: prueba ${n + 3 - n % 3}.`);
    const result = RULES[rule].run(f, lower, upper, n);
    const reference = N.referenceIntegral(f, lower, upper);
    const error = Math.abs(reference - result.value), relative = reference !== 0 ? error / Math.abs(reference) : null;
    const graph = curve(f, lower, upper, 300);
    // Lo que la regla integra en realidad: rectas (trapecio) o parábolas/cúbicas por tramos (Simpson).
    const pieces = {x: [], y: []}, block = rule === 'trapezoid' ? 1 : rule === 'simpson13' ? 2 : 3;
    for (let start = 0; start < n; start += block) {
      const nodes = result.x.slice(start, start + block + 1).map((x, i) => [x, result.y[start + i]]);
      const local = curve(x => N.lagrange(nodes, x).value, nodes[0][0], nodes[nodes.length - 1][0], block === 1 ? 2 : 24);
      pieces.x.push(...local.x); pieces.y.push(...local.y);
    }
    const romberg = N.romberg(f, lower, upper, 5);
    const convergence = [1, 2, 4, 8, 16, 32].map(k => k * block).map(k => ({n: k, value: RULES[rule].run(f, lower, upper, k).value}));
    const good = relative != null ? relative < 1e-3 : error < 1e-6;
    return {
      status: {kind: good ? 'ok' : relative < 0.05 ? 'warn' : 'bad',
               text: `${RULES[rule].label} con n = ${n} (h = ${fmt(result.h, 5)}): I ≈ ${fmt(result.value, 8)}, error ${pct(relative)}. ${good ? 'Coincide con la referencia en al menos tres cifras.' : 'Aumenta n o usa una regla de mayor orden.'}`},
      metrics: [{label: 'Integral aproximada', value: fmt(result.value, 8)}, {label: 'Referencia (Romberg fino)', value: fmt(reference, 8)},
                {label: 'Error verdadero', value: fmt(error, 3), tone: good ? 'good' : 'bad'}, {label: 'Error relativo', value: pct(relative)}],
      cards: [
        {title: 'Área que calcula la regla', note: 'Zona sombreada: lo que integra la regla. Curva continua: la función. La diferencia entre ambas es el error.',
         plot: {traces: [
           line(pieces.x, pieces.y, 'Aproximación por tramos', {fill: 'tozeroy', fillcolor: 'rgba(87,70,187,0.16)', line: {color: COLORS[0], width: 1.6}}),
           line(graph.x, graph.y, 'f(x)', {line: {color: COLORS[1], width: 2.6}}),
           dots(result.x, result.y, 'Nodos', {marker: {size: 7, color: '#172544'}}),
         ]}},
        {title: 'Convergencia al duplicar n', note: `Regla de orden O(h^${RULES[rule].order}): cada vez que n se duplica, el error debería dividirse entre ${2 ** RULES[rule].order}.`,
         table: {columns: ['n', 'Integral', 'Error', 'Razón de errores'], rows: convergence.map((item, i) => {
           const current = Math.abs(reference - item.value), previous = i ? Math.abs(reference - convergence[i - 1].value) : null;
           return [String(item.n), fmt(item.value, 9), fmt(current, 3), previous && current > 1e-14 ? fmt(previous / current, 4) : '—'];
         })}},
        {title: 'Tabla de Romberg', note: 'Primera columna: trapecio con 1, 2, 4, 8 y 16 segmentos. Cada columna a la derecha elimina un orden del error.',
         table: {columns: ['n', 'O(h²)', 'O(h⁴)', 'O(h⁶)', 'O(h⁸)', 'O(h¹⁰)'], keyCells: [[4, 5]],
                 rows: romberg.table.map((row, i) => [String(2 ** i), ...Array.from({length: 5}, (_, k) => k < row.length ? fmt(row[k], 9) : '')])}},
      ],
    };
  },
};

export const differentiation = {
  presets: [
    {label: 'Polinomio de grado 4', values: {expression: '-0.1x^4 - 0.15x^3 - 0.5x^2 - 0.25x + 1.2', x: '0.5', h: '0.25'}},
    {label: 'eˣ en x = 1', values: {expression: 'exp(x)', x: '1', h: '0.1'}},
    {label: 'sen(x)·x', values: {expression: 'x*sin(x)', x: '1', h: '0.2'}},
  ],
  fields: [
    {name: 'expression', label: 'Función f(x)', type: 'text', value: '-0.1x^4 - 0.15x^3 - 0.5x^2 - 0.25x + 1.2', hint: FUNCTION_HINT},
    {name: 'x', label: 'Punto x', type: 'number', value: '0.5', half: true},
    {name: 'h', label: 'Paso h', type: 'number', value: '0.25', min: 1e-10, max: 10, half: true},
  ],
  run({expression, x, h}) {
    const f = parseFunction('expression', expression);
    const needed = [x - 2 * h, x - h, x, x + h, x + 2 * h].map(f);
    if (needed.some(value => !Number.isFinite(value))) throw new FieldError('h', 'La función no está definida en algún punto x ± h o x ± 2h. Reduce h o cambia x.');
    const reference = N.referenceDerivative(f, x);
    const rows = N.DIFFERENCE_FORMULAS.map(formula => {
      const value = formula.d(f, x, h), half = formula.d(f, x, h / 2);
      return {formula, value, error: Math.abs(value - reference), halfError: Math.abs(half - reference)};
    });
    const richardson = N.richardson(f, x, h, 2).value;
    const central = rows[2];
    const relative = reference !== 0 ? central.error / Math.abs(reference) : null;
    const span = Math.max(2.6 * h, 0.5);
    const graph = curve(f, x - span, x + span);
    const fx = f(x);
    const tangent = slope => ({x: [x - span, x + span], y: [fx - slope * span, fx + slope * span]});
    const secant = (x0, x1, name, color) => line([x0, x1], [f(x0), f(x1)], name, {mode: 'lines+markers', marker: {size: 8}, line: {color, width: 2.2}});
    const steps = Array.from({length: 13}, (_, i) => 10 ** (-i * 0.75));
    const errorCurve = index => {
      const errors = steps.map(step => Math.abs(N.DIFFERENCE_FORMULAS[index].d(f, x, step) - reference));
      return line(steps, errors.map(value => value > 0 ? value : null), N.DIFFERENCE_FORMULAS[index].label, {mode: 'lines+markers', marker: {size: 6}, line: {color: COLORS[index === 0 ? 1 : 0], width: 2.2}});
    };
    const exact = tangent(reference);
    const good = relative != null ? relative < 0.01 : central.error < 1e-6;
    return {
      status: {kind: good ? 'ok' : 'warn', text: `Con h = ${fmt(h)}, la diferencia centrada da f′(${fmt(x)}) ≈ ${fmt(central.value, 7)} (error ${pct(relative)}). Richardson con h y h/2 lo mejora a ${fmt(richardson, 8)}.`},
      metrics: [{label: 'Referencia f′(x)', value: fmt(reference, 8)}, {label: 'Centrada', value: fmt(central.value, 8), tone: good ? 'good' : null},
                {label: 'Richardson', value: fmt(richardson, 8), tone: 'good', hint: `Error ${fmt(Math.abs(richardson - reference), 2)}`},
                {label: 'f″(x) centrada', value: fmt(N.secondDerivative(f, x, h), 7)}],
      cards: [
        {title: 'Secantes que aproximan la tangente', note: 'La pendiente de cada secante es la derivada estimada. La recta gris es la tangente de referencia.',
         plot: {traces: [
           line(graph.x, graph.y, 'f(x)', {line: {color: '#172544', width: 2.6}}),
           line(exact.x, exact.y, 'Tangente (referencia)', {line: {color: '#9aa5bb', width: 2, dash: 'dash'}}),
           secant(x, x + h, 'Hacia adelante', COLORS[1]), secant(x - h, x, 'Hacia atrás', COLORS[2]), secant(x - h, x + h, 'Centrada', COLORS[0]),
           dots([x], [fx], 'Punto x', {marker: {size: 11, color: '#1f7a48'}}),
         ]}},
        {title: 'Comparación de fórmulas', note: 'La razón compara el error con h y con h/2: cerca de 2 para O(h), de 4 para O(h²) y de 16 para O(h⁴).',
         table: {columns: ['Fórmula', 'Orden', `f′ con h = ${fmt(h)}`, 'Error', 'Error con h/2', 'Razón'], keyRows: [2],
                 rows: rows.map(row => [row.formula.label, `O(h${row.formula.order > 1 ? '^' + row.formula.order : ''})`, fmt(row.value, 8), fmt(row.error, 3), fmt(row.halfError, 3),
                                        row.halfError > 1e-13 ? fmt(row.error / row.halfError, 4) : '—'])}},
        {title: 'Error frente al paso h', note: 'Ambos ejes en escala logarítmica. Al reducir h baja el truncamiento, hasta que el redondeo hace que el error vuelva a subir.',
         plot: {small: true, traces: [errorCurve(0), errorCurve(2)],
                layout: {xaxis: {title: 'Paso h', type: 'log', autorange: 'reversed'}, yaxis: {title: 'Error absoluto', type: 'log'}}}},
        {title: 'Derivadas de orden superior', table: {columns: ['Derivada', 'Fórmula centrada', 'Valor'], rows: [
          ['f″(x)', '[f(x+h) − 2f(x) + f(x−h)] / h²', fmt(N.secondDerivative(f, x, h), 8)],
          ['f‴(x)', '[f(x+2h) − 2f(x+h) + 2f(x−h) − f(x−2h)] / (2h³)', fmt(N.thirdDerivative(f, x, h), 8)]]}},
      ],
    };
  },
};
