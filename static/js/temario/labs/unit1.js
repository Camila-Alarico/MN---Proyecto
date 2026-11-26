// Unidad 1 · Aproximación y errores: diana de exactitud/precisión y polinomio de Taylor.
import * as N from '../numeric.js';
import {COLORS, curve, dots, fmt, line, pct} from './framework.js';

export const precision = {
  presets: [
    {label: 'Preciso e inexacto', values: {bias: 0.5, spread: 0.06}},
    {label: 'Exacto y preciso', values: {bias: 0, spread: 0.06}},
    {label: 'Exacto e impreciso', values: {bias: 0, spread: 0.38}},
    {label: 'Ni exacto ni preciso', values: {bias: 0.5, spread: 0.38}},
  ],
  fields: [
    {name: 'bias', label: 'Sesgo (error sistemático)', type: 'range', min: 0, max: 0.8, step: 0.02, value: 0.5, format: v => v.toFixed(2),
     hint: 'Desplaza todo el grupo: un instrumento mal calibrado.'},
    {name: 'spread', label: 'Dispersión (error aleatorio)', type: 'range', min: 0.02, max: 0.5, step: 0.02, value: 0.06, format: v => v.toFixed(2),
     hint: 'Separa los disparos entre sí: poca repetibilidad.'},
    {name: 'count', label: 'Número de disparos', type: 'range', min: 5, max: 60, step: 1, value: 20},
  ],
  run({bias, spread, count}) {
    const result = N.shots(count, bias, spread);
    const accurate = result.inaccuracy < 0.15, precise = result.imprecision < 0.2;
    const ring = radius => ({type: 'circle', xref: 'x', yref: 'y', x0: -radius, x1: radius, y0: -radius, y1: radius,
                             line: {color: '#c9cfdf', width: 1}, fillcolor: radius === 0.15 ? '#e8f6ed' : 'rgba(0,0,0,0)', layer: 'below'});
    return {
      status: {kind: accurate && precise ? 'ok' : accurate || precise ? 'warn' : 'bad',
               text: `${accurate ? 'Exacto' : 'Inexacto'} ${precise ? 'y preciso' : 'e impreciso'}: ` +
                     (accurate && precise ? 'el grupo es compacto y está centrado en el valor verdadero.'
                       : accurate ? 'el promedio acierta, pero cada disparo individual es poco fiable.'
                       : precise ? 'los disparos se repiten muy bien… en el lugar equivocado. Hay un error sistemático.'
                       : 'el grupo está desplazado y además disperso.')},
      metrics: [
        {label: 'Inexactitud (sesgo)', value: fmt(result.inaccuracy, 3), hint: 'Distancia del promedio al centro', tone: accurate ? 'good' : 'bad'},
        {label: 'Imprecisión (dispersión)', value: fmt(result.imprecision, 3), hint: 'Distancia típica al promedio', tone: precise ? 'good' : 'bad'},
        {label: 'Disparos', value: String(count)},
      ],
      cards: [{title: 'Diana: el centro es el valor verdadero', note: 'La cruz marca el promedio de los disparos; la zona verde, la tolerancia de exactitud.',
        plot: {traces: [
          dots(result.points.map(p => p.x), result.points.map(p => p.y), 'Disparos', {marker: {size: 9, color: COLORS[0], opacity: 0.75}}),
          dots([result.mean.x], [result.mean.y], 'Promedio', {marker: {size: 15, symbol: 'x', color: COLORS[1], line: {width: 2}}}),
          dots([0], [0], 'Valor verdadero', {marker: {size: 10, symbol: 'circle-open', color: '#1f7a48', line: {width: 3}}}),
          line([0, result.mean.x], [0, result.mean.y], 'Sesgo', {line: {color: COLORS[1], width: 2, dash: 'dot'}}),
        ], layout: {xaxis: {range: [-1.5, 1.5], title: ''}, yaxis: {range: [-1.5, 1.5], scaleanchor: 'x', title: ''},
                    shapes: [0.15, 0.5, 1, 1.4].map(ring)}}}],
    };
  },
};

export const taylor = {
  presets: [
    {label: 'eˣ en x = 1', values: {fn: 'exp', a: '0', x: '1', order: 5}},
    {label: 'cos(x) en π/3', values: {fn: 'cos', a: '0', x: '1.047198', order: 4}},
    {label: 'sen(x) lejos de a', values: {fn: 'sin', a: '0', x: '4', order: 5}},
    {label: 'ln(1+x): diverge', values: {fn: 'ln', a: '0', x: '1.5', order: 8}},
  ],
  fields: [
    {name: 'fn', label: 'Función', type: 'select', value: 'exp', options: Object.entries(N.TAYLOR_FUNCTIONS).map(([key, item]) => [key, item.label])},
    {name: 'a', label: 'Punto de expansión a', type: 'number', value: '0', half: true},
    {name: 'x', label: 'Evaluar en x', type: 'number', value: '1', half: true},
    {name: 'order', label: 'Orden del polinomio n', type: 'range', min: 0, max: 12, step: 1, value: 5, hint: 'Cada orden añade un término de la serie.'},
  ],
  run({fn, a, x, order}) {
    const result = N.taylor(fn, a, x, order);
    const item = N.TAYLOR_FUNCTIONS[fn];
    const span = Math.max(1.5, Math.abs(x - a) * 1.4);
    let from = Math.min(a, x) - span * 0.6, to = Math.max(a, x) + span * 0.6;
    if (fn === 'ln') from = Math.max(from, -0.95);
    const exact = curve(item.f, from, to), approx = curve(result.polynomial, from, to);
    const finite = exact.y.filter(value => value != null);
    const low = Math.min(...finite), high = Math.max(...finite), pad = Math.max(0.5, (high - low) * 0.35);
    const errors = result.terms.map(term => term.error);
    const growing = errors.length > 3 && errors[errors.length - 1] > errors[errors.length - 3] && errors[errors.length - 1] > 1e-9;
    const relative = result.exact !== 0 ? result.error / Math.abs(result.exact) : null;
    return {
      status: growing ? {kind: 'bad', text: 'El error crece al añadir términos: x está fuera del radio de convergencia de la serie.'}
        : relative != null && relative < 0.01 ? {kind: 'ok', text: `Con orden ${order} el error relativo es ${pct(relative)}: el polinomio ya reproduce bien la función en x.`}
        : {kind: 'warn', text: `Con orden ${order} el error relativo es ${pct(relative)}. Sube el orden o acerca x al punto a.`},
      metrics: [
        {label: 'Valor verdadero f(x)', value: fmt(result.exact, 8)},
        {label: `Aproximación P${order}(x)`, value: fmt(result.approximation, 8)},
        {label: 'Error de truncamiento', value: fmt(result.error, 4), tone: growing ? 'bad' : relative < 0.01 ? 'good' : null},
        {label: 'Error relativo', value: pct(relative)},
      ],
      cards: [
        {title: 'La función y su polinomio de Taylor', note: 'Cerca de a ambas curvas coinciden; al alejarse, el polinomio se separa.',
         plot: {traces: [
           line(exact.x, exact.y, item.label, {line: {color: COLORS[0], width: 2.6}}),
           line(approx.x, approx.y, `Polinomio de orden ${order}`, {line: {color: COLORS[1], width: 2.4, dash: 'dash'}}),
           line([x, x], [result.exact, result.approximation], 'Error en x', {line: {color: '#b23346', width: 4}}),
           dots([a], [item.f(a)], 'Punto de expansión a', {marker: {size: 11, color: '#1f7a48'}}),
           dots([x], [result.approximation], 'Aproximación', {marker: {size: 11, color: COLORS[1], symbol: 'diamond'}}),
         ], layout: {yaxis: {range: [low - pad, high + pad], title: 'y'}}}},
        {title: 'Término a término', note: 'El error de truncamiento es lo que falta por sumar.',
         table: {columns: ['Orden', 'Término', 'Suma parcial', 'Error verdadero', 'Error relativo'], keyRows: [order],
                 rows: result.terms.map(term => [String(term.k), fmt(term.term, 7), fmt(term.sum, 8), fmt(term.error, 4), pct(term.relative)])}},
      ],
    };
  },
};
