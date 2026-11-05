// Escenas de sistemas lineales: eliminación gaussiana con pivoteo parcial y Gauss-Seidel.
// Se calculan con el mismo caso base que el ejercicio resuelto (A·x = b con solución (1, 2, 3)).
import {ns, ts, sub, sup, sci, el} from './format.js';

export const BASE_A = [[4, 1, 1], [1, 5, 1], [1, 1, 6]];
export const BASE_B = [9, 14, 21];
const fmt = value => ns(Math.abs(value) < 1e-12 ? 0 : value, 6);

function matrix(M, marks = {}) {
  const n = M.length;
  const grid = el('div', {class: 'anim-matrix', style: `--cols:${n + 1}`, role: 'table', 'aria-label': 'Matriz aumentada [A | b]'});
  M.forEach((row, i) => {
    const tr = el('div', {class: `anim-matrix-row${marks.changed === i ? ' is-changed' : ''}${marks.source === i ? ' is-source' : ''}${marks.focus === i ? ' is-focus' : ''}${marks.swap?.includes(i) ? ' is-swap' : ''}`, role: 'row'});
    tr.append(el('span', {class: 'anim-row-label', role: 'rowheader', text: `F${i + 1}`}));
    row.forEach((value, j) => {
      const classes = ['anim-cell'];
      if (j === n) classes.push('is-rhs');
      if (marks.pivot && marks.pivot[0] === i && marks.pivot[1] === j) classes.push('is-pivot');
      if (marks.zero && marks.zero[0] === i && marks.zero[1] === j) classes.push('is-zeroed');
      if (marks.column === j && i >= (marks.fromRow ?? 0)) classes.push('is-column');
      if (marks.diagonal && i === j) classes.push('is-pivot');
      tr.append(el('span', {class: classes.join(' '), role: 'cell', text: fmt(value)}));
    });
    grid.append(tr);
  });
  return grid;
}
function chips(values, {fresh = -1, label = 'x'} = {}) {
  return el('div', {class: 'anim-chips'}, values.map((value, i) => el('span', {class: `anim-chip${value == null ? ' is-empty' : ''}${i === fresh ? ' is-new-chip' : ''}`}, [
    el('small', {text: `${label}${sub(i + 1)}`}), el('strong', {text: value == null ? '?' : fmt(value)}),
  ])));
}
const op = text => el('p', {class: 'anim-operation', text});

// ---- Eliminación gaussiana ---------------------------------------------------------------------
export function gaussFrames(A, b) {
  const n = A.length, M = A.map((row, i) => [...row, b[i]]), frames = [];
  const snap = () => M.map(row => [...row]);
  const push = (frame, marks, x) => {
    const S = snap(), X = x ? [...x] : null;
    frames.push({...frame, render: board => {
      board.append(matrix(S, marks));
      if (frame.op) board.append(op(frame.op));
      if (X) board.append(chips(X, {fresh: marks.fresh}));
    }});
  };
  push({title: 'Matriz aumentada [A | b]', text: 'Se escribe el sistema como una sola tabla: los coeficientes de A a la izquierda y los términos independientes b a la derecha de la barra.', step: 0, row: 0}, {});
  for (let k = 0; k < n - 1; k++) {
    const step = k === 0 ? 0 : 1;
    let p = k;
    for (let i = k + 1; i < n; i++) if (Math.abs(M[i][k]) > Math.abs(M[p][k])) p = i;
    const values = M.slice(k).map(row => fmt(Math.abs(row[k]))).join(', ');
    if (p !== k) {
      push({title: `Columna ${k + 1}: intercambio de filas`, text: `Entre |${values}| el mayor está en la fila ${p + 1}: se intercambian F${k + 1} y F${p + 1} (pivoteo parcial).`, op: `F${k + 1} ↔ F${p + 1}`, step, row: k}, {column: k, fromRow: k, swap: [k, p]});
      [M[k], M[p]] = [M[p], M[k]];
    }
    push({title: `Columna ${k + 1}: elegir el pivote`, text: p === k ? `Entre |${values}| el mayor ya está en la fila ${k + 1}: el pivote es ${fmt(M[k][k])} y no hay intercambio.` : `Tras el intercambio, el pivote es ${fmt(M[k][k])}.`, tex: String.raw`\text{pivote}=a_{${k + 1}${k + 1}}=${ts(M[k][k])}`, step, row: k}, {column: k, fromRow: k, pivot: [k, k]});
    for (let i = k + 1; i < n; i++) {
      const original = M[i][k], m = original / M[k][k];
      for (let j = k; j <= n; j++) M[i][j] -= m * M[k][j];
      M[i][k] = 0;
      const last = i === n - 1;
      push({
        title: `Anular a${sub(i + 1)}${sub(k + 1)}`,
        text: `Multiplicador m${sub(i + 1)}${sub(k + 1)} = ${fmt(original)}/${fmt(M[k][k])} = ${fmt(m)}. Se resta ese múltiplo de la fila pivote para dejar un cero bajo el pivote.`,
        tex: String.raw`m_{${i + 1}${k + 1}}=\frac{${ts(original)}}{${ts(M[k][k])}}=${ts(m)},\qquad F_{${i + 1}}\leftarrow F_{${i + 1}}-${ts(m)}\,F_{${k + 1}}`,
        op: `F${i + 1} ← F${i + 1} − ${fmt(m)}·F${k + 1}  =  (${M[i].map(fmt).slice(0, n).join(', ')} | ${fmt(M[i][n])})`,
        step, row: last ? k + 1 : k,
      }, {pivot: [k, k], source: k, changed: i, zero: [i, k]});
    }
  }
  const x = Array(n).fill(null);
  for (let i = n - 1; i >= 0; i--) {
    let s = M[i][n];
    const terms = [];
    for (let j = i + 1; j < n; j++) {s -= M[i][j] * x[j]; terms.push(`${ts(M[i][j])}\\cdot${ts(x[j])}`);}
    x[i] = s / M[i][i];
    push({
      title: `Sustitución hacia atrás: x${sub(i + 1)}`,
      text: `La fila ${i + 1} tiene una sola incógnita nueva: x${sub(i + 1)} = ${fmt(x[i])}.`,
      tex: String.raw`x_{${i + 1}}=\frac{${ts(M[i][n])}${terms.length ? '-' + terms.join('-') : ''}}{${ts(M[i][i])}}=${ts(x[i])}`,
      step: 2, row: i === 0 ? 3 : 2,
    }, {focus: i, fresh: i}, x);
  }
  const checks = A.map((row, i) => `${row.map((a, j) => `${a}(${ts(x[j])})`).join(' + ')} = ${ts(row.reduce((s, a, j) => s + a * x[j], 0))}`);
  const residual = Math.max(...A.map((row, i) => Math.abs(b[i] - row.reduce((s, a, j) => s + a * x[j], 0))));
  frames.push({
    title: 'Verificar la solución',
    text: `Al sustituir x = (${x.map(v => ts(v)).join(', ')}) en las ecuaciones originales: ${checks.join('; ')}. El residuo ‖b − A·x‖∞ = ${sci(residual, 1)}.`,
    tex: String.raw`r=b-Ax=(${A.map(() => '0').join(',')})`,
    step: 3, row: 3,
    render: board => {
      board.append(matrix(A.map((row, i) => [...row, b[i]]), {}));
      board.append(el('ul', {class: 'anim-checks'}, checks.map(text => el('li', {text: `✓ ${text}`}))));
      board.append(chips(x));
    },
  });
  return frames;
}

// ---- Gauss-Seidel -------------------------------------------------------------------------------
const residualOf = (A, b, x) => Math.max(...A.map((row, i) => Math.abs(b[i] - row.reduce((s, a, j) => s + a * x[j], 0))));
export function seidelHistory(A, b, tol = 1e-6, max = 100) {
  const n = A.length, x = Array(n).fill(0), history = [{k: 0, x: [...x], step: null, res: residualOf(A, b, x)}];
  for (let k = 1; k <= max; k++) {
    const old = [...x], parts = [];
    for (let i = 0; i < n; i++) {
      let s = b[i];
      const terms = [];
      for (let j = 0; j < n; j++) if (j !== i) {s -= A[i][j] * x[j]; terms.push({j, a: A[i][j], v: x[j], fresh: j < i});}
      x[i] = s / A[i][i];
      parts.push({i, terms, value: x[i]});
    }
    const step = Math.max(...x.map((v, i) => Math.abs(v - old[i]))), res = residualOf(A, b, x);
    history.push({k, x: [...x], old, parts, step, res});
    if (step <= tol && res <= tol) break;
  }
  return history;
}
function residualChart(history, upto) {
  const scale = res => Math.max(4, Math.min(100, (Math.log10(Math.max(res, 1e-8)) + 8) / 10 * 100));
  return el('div', {class: 'anim-residuals', 'aria-label': 'Residuo por iteración, escala logarítmica'}, [
    el('span', {class: 'anim-residuals-title', text: 'Residuo ‖b − A·x‖∞ (escala log)'}),
    el('div', {class: 'anim-residual-bars'}, history.filter(h => h.k <= upto).map(h => el('span', {class: `anim-residual${h.k === upto ? ' is-current' : ''}`, style: `--h:${scale(h.res)}%`, title: `k = ${h.k}: ${sci(h.res, 2)}`}, [
      el('i', {}), el('small', {text: String(h.k)}),
    ]))),
  ]);
}
export function seidelFrames(A, b) {
  const n = A.length, history = seidelHistory(A, b), frames = [];
  const dominance = A.map((row, i) => ({d: Math.abs(row[i]), s: row.reduce((t, a, j) => t + (j === i ? 0 : Math.abs(a)), 0)}));
  frames.push({
    title: 'Comprobar la dominancia diagonal',
    text: `${dominance.map(({d, s}) => `${ts(d)} > ${ts(s)}`).join(', ')}: cada elemento de la diagonal supera la suma de los demás de su fila. La convergencia está garantizada desde cualquier inicio; se parte de x⁽⁰⁾ = (0, 0, 0).`,
    tex: String.raw`|a_{ii}|>\sum_{j\ne i}|a_{ij}|`,
    step: 0, row: 0,
    render: board => {
      board.append(matrix(A.map((row, i) => [...row, b[i]]), {diagonal: true}));
      board.append(el('ul', {class: 'anim-checks'}, dominance.map(({d, s}, i) => el('li', {text: `${d > s ? '✓' : '✗'} Fila ${i + 1}: ${ts(d)} > ${ts(s)}`}))));
      board.append(chips(history[0].x));
    },
  });
  const first = history[1];
  first.parts.forEach(part => {
    const values = first.x.map((v, i) => (i <= part.i ? v : first.old[i]));
    const fresh = part.terms.filter(t => t.fresh);
    const texTerms = part.terms.map(t => `-${ts(t.a)}\\cdot${t.fresh ? `\\mathbf{${ts(t.v)}}` : ts(t.v)}`).join('');
    frames.push({
      title: `Iteración 1: x${sub(part.i + 1)}`,
      text: `x${sub(part.i + 1)} = ${fmt(part.value)}.${fresh.length ? ` Usa ${fresh.map(t => `x${sub(t.j + 1)} = ${fmt(t.v)}`).join(' y ')} recién calculado${fresh.length > 1 ? 's' : ''} en esta misma iteración (en negrita): esa es la diferencia con Jacobi.` : ' Todavía solo hay valores del vector inicial.'}`,
      tex: String.raw`x_{${part.i + 1}}^{(1)}=\frac{${ts(b[part.i])}${texTerms}}{${ts(A[part.i][part.i])}}=${ts(part.value)}`,
      step: 1, row: 1,
      render: board => {
        board.append(chips(values, {fresh: part.i}));
        board.append(op(`x${sub(part.i + 1)} ← (${ts(b[part.i])} ${part.terms.map(t => `− ${ts(t.a)}·${fmt(t.v)}`).join(' ')}) / ${ts(A[part.i][part.i])}`));
        board.append(residualChart(history, part.i === n - 1 ? 1 : 0));
      },
    });
  });
  const iterationFrame = (h, row) => ({
    title: `Iteración ${h.k}`,
    text: `x⁽${sup(h.k)}⁾ = (${h.x.map(fmt).join(', ')}). Paso ‖Δx‖∞ = ${fmt(h.step)} y residuo ‖r‖∞ = ${fmt(h.res)}.${h.step <= 1e-6 && h.res <= 1e-6 ? ' Ambos son ≤ 10⁻⁶: el método se detiene.' : ''}`,
    tex: String.raw`\|\Delta x\|_\infty=${ts(h.step)},\qquad\|b-Ax^{(${h.k})}\|_\infty=${ts(h.res)}`,
    step: 2, row,
    render: board => {
      board.append(chips(h.x, {fresh: -1}));
      board.append(op(`antes: (${h.old.map(fmt).join(', ')})  →  ahora: (${h.x.map(fmt).join(', ')})`));
      board.append(residualChart(history, h.k));
    },
  });
  history.slice(2, 5).forEach(h => frames.push(iterationFrame(h, h.k)));
  const last = history[history.length - 1];
  if (last.k > 4) frames.push({...iterationFrame(last, -1), title: `Iteración ${last.k}: se alcanza la tolerancia`});
  return frames;
}

export const linearScenes = {
  gauss: () => ({kind: 'html', title: 'Eliminación gaussiana sobre el caso base', frames: gaussFrames(BASE_A, BASE_B)}),
  seidel: () => ({kind: 'html', title: 'Gauss-Seidel sobre el caso base', frames: seidelFrames(BASE_A, BASE_B)}),
};
