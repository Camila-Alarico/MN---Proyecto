// Unidad 3 · Sistemas lineales: Gauss-Jordan e inversa, descomposición LU, Jacobi frente a Gauss-Seidel.
import * as N from '../numeric.js';
import {COLORS, fmt, line, parseSystem} from './framework.js';

const BASE = '4 1 1 | 9\n1 5 1 | 14\n1 1 6 | 21';
const SYSTEM_HINT = 'Una ecuación por línea: coeficientes separados por espacios y, tras «|», el término independiente.';
const solutionMetrics = x => x.slice(0, 6).map((value, i) => ({label: `x${i + 1}`, value: fmt(value, 8)}));

export const gaussjordan = {
  presets: [
    {label: 'Caso base', values: {system: BASE, mode: 'solve'}},
    {label: 'Inversa del caso base', values: {system: BASE, mode: 'inverse'}},
    {label: 'Exige intercambio', values: {system: '0 2 1 | 7\n1 1 1 | 6\n2 1 3 | 13', mode: 'solve'}},
    {label: 'Singular', values: {system: '1 2 | 3\n2 4 | 6', mode: 'solve'}},
  ],
  fields: [
    {name: 'system', label: 'Sistema [A | b]', type: 'textarea', value: BASE, rows: 4, hint: SYSTEM_HINT},
    {name: 'mode', label: '¿Qué calcular?', type: 'select', value: 'solve', options: [['solve', 'Solución de A·x = b'], ['inverse', 'Matriz inversa A⁻¹']]},
  ],
  run({system, mode}) {
    const inverse = mode === 'inverse';
    const {matrix, vector, n} = parseSystem('system', system, {needVector: !inverse});
    const result = inverse ? N.inverse(matrix) : N.gaussJordan(matrix, vector.map(value => [value]));
    const steps = result.steps.map((step, index) => ({label: `${index}. ${step.label}`, data: step.matrix, sep: n}));
    if (inverse) {
      const product = N.matMul(matrix, result.result);
      const defect = Math.max(...product.flatMap((row, i) => row.map((value, j) => Math.abs(value - (i === j ? 1 : 0)))));
      return {
        status: {kind: 'ok', text: `[A | I] se redujo a [I | A⁻¹] en ${result.steps.length - 1} operaciones de fila. Comprobación: A·A⁻¹ = I con error ${fmt(defect, 2)}.`},
        metrics: [{label: 'Tamaño', value: `${n} × ${n}`}, {label: 'Operaciones de fila', value: String(result.steps.length - 1)},
                  {label: '‖A·A⁻¹ − I‖', value: fmt(defect, 2), tone: 'good'}],
        cards: [{title: 'Matriz inversa', matrices: [{label: 'A⁻¹', data: result.result}]},
                {title: 'Operaciones de fila', note: 'La línea punteada separa A de la identidad que se transforma en la inversa.', matrices: steps}],
      };
    }
    const x = result.result.map(row => row[0]);
    const residual = N.residual(matrix, x, vector);
    return {
      status: {kind: 'ok', text: `La matriz aumentada se redujo a [I | x] en ${result.steps.length - 1} operaciones de fila. Residuo ‖b − A·x‖ = ${fmt(residual, 2)}.`},
      metrics: [...solutionMetrics(x), {label: 'Residuo ‖b − A·x‖∞', value: fmt(residual, 2), tone: 'good'}],
      cards: [{title: 'Operaciones de fila', note: 'Cada bloque es la matriz aumentada después de la operación indicada.', matrices: steps}],
    };
  },
};

export const lu = {
  presets: [
    {label: 'Caso base', values: {system: BASE}},
    {label: 'Con pivoteo', values: {system: '1 2 3 | 14\n4 5 6 | 32\n7 8 10 | 53'}},
    {label: '4 × 4', values: {system: '4 -1 0 0 | 3\n-1 4 -1 0 | 2\n0 -1 4 -1 | 2\n0 0 -1 4 | 3'}},
  ],
  fields: [{name: 'system', label: 'Sistema [A | b]', type: 'textarea', value: BASE, rows: 4, hint: SYSTEM_HINT}],
  run({system}) {
    const {matrix, vector, n} = parseSystem('system', system);
    const result = N.luDecomposition(matrix, vector);
    const permuted = result.permutation.some((value, index) => value !== index);
    const pa = result.permutation.map(index => matrix[index]);
    const product = N.matMul(result.lower, result.upper);
    const defect = Math.max(...product.flatMap((row, i) => row.map((value, j) => Math.abs(value - pa[i][j]))));
    const residual = N.residual(matrix, result.solution, vector);
    return {
      status: {kind: 'ok', text: `${permuted ? 'P·A = L·U (hubo intercambio de filas)' : 'A = L·U'}; comprobación ‖L·U − ${permuted ? 'P·A' : 'A'}‖ = ${fmt(defect, 2)}. La solución sale de dos sustituciones.`},
      metrics: [...solutionMetrics(result.solution), {label: 'det(A)', value: fmt(result.determinant, 8)},
                {label: 'Residuo ‖b − A·x‖∞', value: fmt(residual, 2), tone: 'good'}],
      cards: [
        {title: 'Factores', note: 'L guarda los multiplicadores; U es la matriz triangular que deja la eliminación.',
         matrices: [{label: 'L (triangular inferior)', data: result.lower}, {label: 'U (triangular superior)', data: result.upper},
                    ...(permuted ? [{label: 'Orden de filas P', data: result.permutation.map(index => [index + 1])}] : [])]},
        {title: 'Cómo se obtuvieron', steps: result.steps.length ? result.steps : ['La matriz ya era triangular superior: no hizo falta eliminar.']},
        {title: 'Dos sustituciones', note: 'Primero L·d = b hacia adelante; después U·x = d hacia atrás.',
         table: {columns: ['i', permuted ? 'bᵢ (permutado)' : 'bᵢ', 'dᵢ', 'xᵢ'],
                 rows: result.solution.map((value, i) => [String(i + 1), fmt(result.pb[i], 8), fmt(result.d[i], 8), fmt(value, 8)])}},
      ],
    };
  },
};

export const iterative = {
  presets: [
    {label: 'Caso base', values: {system: BASE, relaxation: 1}},
    {label: 'Filas 1 y 2 cambiadas', values: {system: '1 5 1 | 14\n4 1 1 | 9\n1 1 6 | 21', relaxation: 1}},
    {label: 'Tridiagonal', values: {system: '2 -1 0 0 | 1\n-1 2 -1 0 | 0\n0 -1 2 -1 | 0\n0 0 -1 2 | 1', relaxation: 1.2}},
  ],
  fields: [
    {name: 'system', label: 'Sistema [A | b]', type: 'textarea', value: BASE, rows: 4, hint: SYSTEM_HINT},
    {name: 'tolerance', label: 'Tolerancia', type: 'number', value: '1e-6', min: 1e-14, max: 1, half: true},
    {name: 'maxIterations', label: 'Máx. iteraciones', type: 'number', value: '100', min: 1, max: 500, integer: true, half: true},
    {name: 'relaxation', label: 'Relajación λ (Gauss-Seidel)', type: 'range', min: 0.5, max: 1.9, step: 0.05, value: 1, format: v => v.toFixed(2),
     hint: 'λ = 1 es Gauss-Seidel puro; λ > 1 sobrerrelaja.'},
  ],
  run({system, tolerance, maxIterations, relaxation}) {
    const {matrix, vector} = parseSystem('system', system);
    const options = {tolerance, maxIterations};
    const jacobi = N.iterate(matrix, vector, {...options, seidel: false});
    const seidel = N.iterate(matrix, vector, {...options, seidel: true, relaxation});
    const dominance = N.diagonalDominance(matrix);
    const describe = run => run.converged ? `${run.iterations.length - 1} iteraciones` : run.diverged ? 'diverge' : 'no converge';
    const seidelName = relaxation === 1 ? 'Gauss-Seidel' : `Gauss-Seidel (λ = ${relaxation.toFixed(2)})`;
    const both = jacobi.converged && seidel.converged;
    const residualTrace = (run, name, color) => {
      const usable = run.iterations.filter(it => it.residual > 0 && Number.isFinite(it.residual));
      return line(usable.map(it => it.k), usable.map(it => it.residual), name, {mode: 'lines+markers', marker: {size: 6}, line: {color, width: 2.4}});
    };
    const rows = [];
    const count = Math.min(Math.max(jacobi.iterations.length, seidel.iterations.length), 16);
    const vectorText = it => it ? it.x.map(value => fmt(value, 6)).join(', ') : '';
    for (let k = 0; k < count; k++) {
      rows.push([String(k), vectorText(jacobi.iterations[k]), jacobi.iterations[k] ? fmt(jacobi.iterations[k].residual, 3) : '',
                 vectorText(seidel.iterations[k]), seidel.iterations[k] ? fmt(seidel.iterations[k].residual, 3) : '']);
    }
    const best = seidel.converged ? seidel : jacobi.converged ? jacobi : null;
    return {
      status: both
        ? {kind: 'ok', text: `Ambos convergen: Jacobi en ${jacobi.iterations.length - 1} iteraciones y ${seidelName} en ${seidel.iterations.length - 1}. ${dominance.strict ? 'La matriz es diagonalmente dominante.' : 'Convergen aunque la matriz no es diagonalmente dominante.'}`}
        : best ? {kind: 'warn', text: `Jacobi: ${describe(jacobi)}. ${seidelName}: ${describe(seidel)}. ${dominance.strict ? '' : 'Sin dominancia diagonal no hay garantía de convergencia.'}`}
        : {kind: 'bad', text: `Ninguno converge (Jacobi: ${describe(jacobi)}; ${seidelName}: ${describe(seidel)}). ${dominance.strict ? 'Sube el máximo de iteraciones.' : 'La matriz no es diagonalmente dominante: reordena las ecuaciones.'}`},
      metrics: [
        {label: 'Jacobi', value: describe(jacobi), tone: jacobi.converged ? 'good' : 'bad'},
        {label: seidelName, value: describe(seidel), tone: seidel.converged ? 'good' : 'bad'},
        {label: 'Dominancia diagonal', value: dominance.strict ? 'Estricta' : 'No', tone: dominance.strict ? 'good' : 'bad',
         hint: dominance.rows.map((row, i) => `F${i + 1}: ${fmt(row.diagonal, 4)} ${row.strict ? '>' : '≤'} ${fmt(row.off, 4)}`).join(' · ')},
        ...(best ? best.solution.slice(0, 4).map((value, i) => ({label: `x${i + 1}`, value: fmt(value, 7)})) : []),
      ],
      cards: [
        {title: 'Residuo por iteración', note: 'Escala logarítmica: una recta descendente indica convergencia lineal; cuanto más inclinada, más rápida.',
         plot: {traces: [residualTrace(jacobi, 'Jacobi', COLORS[1]), residualTrace(seidel, seidelName, COLORS[0])],
                layout: {xaxis: {title: 'Iteración k'}, yaxis: {title: 'Residuo ‖b − A·x‖∞', type: 'log'}}}},
        {title: 'Primeras iteraciones', note: count < Math.max(jacobi.iterations.length, seidel.iterations.length) ? `Se muestran las primeras ${count}.` : 'Vector x en cada iteración.',
         table: {columns: ['k', 'Jacobi: x', 'Residuo', `${seidelName}: x`, 'Residuo'], rows}},
      ],
    };
  },
};
