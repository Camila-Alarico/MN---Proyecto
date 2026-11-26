// Unidad 6 · Ecuaciones diferenciales: Euler/Heun, Runge-Kutta y una introducción a las EDP.
import * as N from '../numeric.js';
import {COLORS, FieldError, fmt, line, parseFunction, pct} from './framework.js';

const ODE_FIELDS = [
  {name: 'expression', label: "Pendiente y′ = f(t, y)", type: 'text', value: '4*exp(0.8*t) - 0.5*y', hint: 'Usa t e y, + − * / ^, sin, cos, exp, ln, sqrt.'},
  {name: 't0', label: 't inicial', type: 'number', value: '0', half: true},
  {name: 'y0', label: 'y(t₀)', type: 'number', value: '2', half: true},
  {name: 'h', label: 'Paso h', type: 'number', value: '1', min: 1e-4, max: 100, half: true},
  {name: 'steps', label: 'Número de pasos', type: 'number', value: '4', min: 1, max: 200, integer: true, half: true},
];
const ODE_PRESETS = [
  {label: 'Ejercicio resuelto', values: {expression: '4*exp(0.8*t) - 0.5*y', t0: '0', y0: '2', h: '1', steps: '4'}},
  {label: 'Enfriamiento', values: {expression: '-0.5*(y - 20)', t0: '0', y0: '90', h: '0.5', steps: '16'}},
  {label: 'Paso demasiado grande', values: {expression: '-3*y', t0: '0', y0: '1', h: '0.8', steps: '10'}},
];
const METHOD_COLORS = {euler: COLORS[1], heun: COLORS[0], midpoint: COLORS[2], ralston: COLORS[5], rk3: COLORS[3], rk4: COLORS[4]};

function odeLab(defaults, choices) {
  return {
    presets: ODE_PRESETS,
    fields: [...ODE_FIELDS, {name: 'methods', label: 'Métodos a comparar', type: 'checks', value: defaults,
                             options: choices.map(key => [key, N.ODE_METHODS[key].label, METHOD_COLORS[key]])}],
    run({expression, t0, y0, h, steps, methods}) {
      const f = parseFunction('expression', expression, ['t', 'y']);
      if (!Number.isFinite(f(t0, y0))) throw new FieldError('expression', 'f(t, y) no está definida en la condición inicial.');
      if (!methods.length) throw new FieldError('methods', 'Elige al menos un método.');
      const reference = N.referenceOde(f, t0, y0, h, steps);
      const runs = methods.map(key => ({key, ...N.ODE_METHODS[key], ...N.solveOde(f, t0, y0, h, steps, key)}));
      const last = reference.y[steps];
      const relative = run => last !== 0 ? Math.abs(run.y[steps] - last) / Math.abs(last) : Math.abs(run.y[steps] - last);
      const best = runs.reduce((a, b) => relative(a) <= relative(b) ? a : b), worst = runs.reduce((a, b) => relative(a) >= relative(b) ? a : b);
      const scale = Math.max(...reference.y.map(Math.abs), 1e-9);
      const unstable = runs.some(run => Math.max(...run.y.map(Math.abs)) > 20 * scale);
      const errorTrace = run => line(run.t.slice(1), run.y.slice(1).map((value, i) => Math.abs(value - reference.y[i + 1]) || null), run.label,
        {mode: 'lines+markers', marker: {size: 6}, line: {color: METHOD_COLORS[run.key], width: 2.2}});
      const stages = N.rk4Stages(f, t0, y0, h);
      const cards = [
        {title: 'Solución numérica frente a la referencia', note: 'La curva gris es la referencia (RK4 con paso muy fino). Cada método avanza de punto en punto.',
         plot: {traces: [line(reference.dense.t, reference.dense.y, 'Referencia', {line: {color: '#9aa5bb', width: 3}}),
                         ...runs.map(run => line(run.t, run.y, run.label, {mode: 'lines+markers', marker: {size: 7}, line: {color: METHOD_COLORS[run.key], width: 2.2}}))],
                layout: {xaxis: {title: 't'}, yaxis: {title: 'y'}}}},
        {title: 'Error en cada paso', note: 'Escala logarítmica: los métodos de mayor orden quedan varias décadas por debajo.',
         plot: {small: true, traces: runs.map(errorTrace), layout: {xaxis: {title: 't'}, yaxis: {title: '|y − referencia|', type: 'log'}}}},
        {title: 'Tabla de valores', table: {columns: ['t', 'Referencia', ...runs.map(run => run.label)],
          rows: reference.t.slice(0, 41).map((t, i) => [fmt(t, 5), fmt(reference.y[i], 8), ...runs.map(run => fmt(run.y[i], 8))])}},
      ];
      if (methods.includes('rk4')) cards.push({title: 'Las cuatro pendientes del primer paso de RK4', steps: [
        ['k₁ =', `f(t₀, y₀) = ${fmt(stages.k1, 7)}`], ['k₂ =', `f(t₀ + h/2, y₀ + h·k₁/2) = ${fmt(stages.k2, 7)}`],
        ['k₃ =', `f(t₀ + h/2, y₀ + h·k₂/2) = ${fmt(stages.k3, 7)}`], ['k₄ =', `f(t₀ + h, y₀ + h·k₃) = ${fmt(stages.k4, 7)}`],
        ['y₁ =', `y₀ + h(k₁ + 2k₂ + 2k₃ + k₄)/6 = ${fmt(stages.next, 8)}`]]});
      return {
        status: unstable ? {kind: 'bad', text: 'La solución numérica crece u oscila mientras la referencia no: el paso h es demasiado grande para este método (inestabilidad). Reduce h.'}
          : {kind: relative(best) < 0.01 ? 'ok' : 'warn', text: runs.length > 1
              ? `En t = ${fmt(reference.t[steps])}: ${best.label} tiene error ${pct(relative(best))} y ${worst.label}, ${pct(relative(worst))}.`
              : `En t = ${fmt(reference.t[steps])}: ${best.label} tiene error ${pct(relative(best))}. Activa otro método para comparar.`},
        metrics: [{label: `Referencia y(${fmt(reference.t[steps])})`, value: fmt(last, 8)},
                  ...runs.map(run => ({label: run.label, value: fmt(run.y[steps], 8), hint: `Error ${pct(relative(run))} · orden ${run.order}`, tone: relative(run) < 0.01 ? 'good' : relative(run) > 0.1 ? 'bad' : null}))],
        cards,
      };
    },
  };
}
export const odeEuler = odeLab(['euler', 'heun'], ['euler', 'heun', 'midpoint']);
export const odeRk = odeLab(['euler', 'midpoint', 'rk4'], ['euler', 'heun', 'midpoint', 'ralston', 'rk3', 'rk4']);

export const pde = {
  presets: [{label: 'Barra: estable', values: {problem: 'heat', lambda: 0.4}}, {label: 'Barra: inestable', values: {problem: 'heat', lambda: 0.56}},
            {label: 'Placa en equilibrio', values: {problem: 'laplace'}}],
  fields: [
    {name: 'problem', label: 'Problema', type: 'select', value: 'heat', options: [['heat', 'Calor en una barra (parabólica)'], ['laplace', 'Placa en equilibrio (elíptica)']]},
    {name: 'lambda', label: 'Barra: λ = α·Δt/Δx²', type: 'range', min: 0.05, max: 0.7, step: 0.01, value: 0.4, format: v => v.toFixed(2), hint: 'El esquema explícito es estable solo si λ ≤ 0.5.'},
    {name: 'time', label: 'Barra: pasos de tiempo', type: 'range', min: 1, max: 80, step: 1, value: 30},
    {name: 'top', label: 'Placa: borde superior °C', type: 'number', value: '100', half: true}, {name: 'bottom', label: 'Placa: borde inferior °C', type: 'number', value: '0', half: true},
    {name: 'left', label: 'Placa: borde izquierdo °C', type: 'number', value: '75', half: true}, {name: 'right', label: 'Placa: borde derecho °C', type: 'number', value: '50', half: true},
    {name: 'relaxation', label: 'Placa: sobrerrelajación λ', type: 'range', min: 1, max: 1.95, step: 0.05, value: 1.5, format: v => v.toFixed(2)},
  ],
  run({problem, lambda, time, top, bottom, left, right, relaxation}) {
    if (problem === 'heat') {
      const result = N.heatExplicit({nodes: 21, lambda, steps: time, initial: x => (x > 0.35 && x < 0.65 ? 100 : 0)});
      const shown = [0, Math.round(time / 4), Math.round(time / 2), time].filter((value, i, list) => list.indexOf(value) === i);
      const peak = Math.max(...result.history[time].map(Math.abs));
      return {
        status: result.stable ? {kind: 'ok', text: `λ = ${lambda.toFixed(2)} ≤ 0.5: el esquema es estable. El pulso de calor se difunde y se suaviza con el tiempo.`}
          : {kind: 'bad', text: `λ = ${lambda.toFixed(2)} > 0.5: el esquema explícito es inestable. Aparecen oscilaciones que crecen en cada paso (máximo actual ${fmt(peak, 4)}).`},
        metrics: [{label: 'λ', value: lambda.toFixed(2), tone: result.stable ? 'good' : 'bad', hint: 'Límite de estabilidad: 0.5'}, {label: 'Pasos de tiempo', value: String(time)},
                  {label: 'Temperatura máxima', value: fmt(peak, 5), tone: peak <= 100.01 ? 'good' : 'bad'}, {label: 'Nodos', value: '21'}],
        cards: [
          {title: 'Perfil de temperatura en la barra', note: 'Extremos a 0 °C y un pulso central de 100 °C en t = 0.',
           plot: {traces: shown.map((step, i) => line(result.x, result.history[step], `Paso ${step}`, {line: {color: COLORS[i], width: i === shown.length - 1 ? 3 : 1.8}})),
                  layout: {xaxis: {title: 'Posición x'}, yaxis: {title: 'Temperatura'}}}},
          {title: 'Evolución en el tiempo', note: 'Cada fila es un paso de tiempo; el color indica la temperatura.',
           plot: {small: true, traces: [{type: 'heatmap', z: result.history, x: result.x, colorscale: 'RdBu', zmid: 50, colorbar: {thickness: 12}}],
                  layout: {xaxis: {title: 'Posición x'}, yaxis: {title: 'Paso de tiempo'}}}},
        ],
      };
    }
    const result = N.laplacePlate({size: 13, top, bottom, left, right, relaxation});
    const small = N.laplacePlate({size: 5, top, bottom, left, right, relaxation: 1});
    return {
      status: result.converged ? {kind: 'ok', text: `Liebmann convergió en ${result.iterations} iteraciones con λ = ${relaxation.toFixed(2)}. Cada nodo interior es el promedio de sus cuatro vecinos.`}
        : {kind: 'bad', text: 'El método no alcanzó la tolerancia: prueba un factor de relajación menor.'},
      metrics: [{label: 'Iteraciones', value: String(result.iterations), tone: result.converged ? 'good' : 'bad', hint: 'Prueba λ entre 1.0 y 1.9'},
                {label: 'Temperatura central', value: fmt(result.grid[6][6], 6)}, {label: 'Malla', value: '13 × 13'}],
      cards: [
        {title: 'Temperatura de equilibrio en la placa', plot: {traces: [{type: 'heatmap', z: result.grid, colorscale: 'RdBu', colorbar: {thickness: 12, title: {text: '°C'}}}],
          layout: {xaxis: {title: 'x', constrain: 'domain'}, yaxis: {title: 'y', scaleanchor: 'x'}}}},
        {title: 'Convergencia del método de Liebmann', plot: {small: true, traces: [line(result.changes.map((_, i) => i + 1), result.changes, 'Cambio máximo', {line: {color: COLORS[0], width: 2.4}})],
          layout: {xaxis: {title: 'Iteración'}, yaxis: {title: 'Cambio máximo', type: 'log'}, showlegend: false}}},
        {title: 'Malla gruesa de 3 × 3 nodos interiores', note: 'La misma placa con la malla del ejercicio resuelto (fila superior junto al borde de arriba).',
         table: {columns: ['Fila', 'Columna 1', 'Columna 2', 'Columna 3'], rows: [3, 2, 1].map((i, r) => [['Superior', 'Central', 'Inferior'][r], ...[1, 2, 3].map(j => fmt(small.grid[i][j], 4))])}},
      ],
    };
  },
};
