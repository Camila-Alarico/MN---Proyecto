// Algoritmos del temario (semanas 1 a 16). Funciones puras, sin DOM: los laboratorios
// las usan en el navegador y tests/temario-numeric.test.cjs las comprueba con Node.

export class NumericError extends Error {}
const EPS = 1e-12;
const clone = matrix => matrix.map(row => row.slice());
export const linspace = (a, b, n) => Array.from({length: n}, (_, i) => a + (b - a) * i / (n - 1));

export function fmt(value, digits = 6) {
  if (value == null || Number.isNaN(value)) return '—';
  if (!Number.isFinite(value)) return value > 0 ? '∞' : '−∞';
  if (value === 0) return '0';
  const magnitude = Math.abs(value);
  const text = magnitude >= 1e6 || magnitude < 1e-4 ? value.toExponential(Math.max(1, digits - 3)) : String(Number(value.toPrecision(digits)));
  return text.replace(/-/g, '−');
}

// --- Semana 1: exactitud y precisión ------------------------------------------------
/** Generador determinista (mulberry32): los mismos datos producen los mismos disparos. */
export function seededRandom(seed) {
  let state = seed >>> 0;
  return () => {
    state = (state + 0x6D2B79F5) >>> 0;
    let t = state;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
export function shots(count, bias, spread, seed = 7) {
  const random = seededRandom(seed);
  const normal = () => Math.sqrt(-2 * Math.log(1 - random())) * Math.cos(2 * Math.PI * random());
  const points = Array.from({length: count}, () => ({x: bias + spread * normal(), y: bias * 0.6 + spread * normal()}));
  const mean = {x: points.reduce((s, p) => s + p.x, 0) / count, y: points.reduce((s, p) => s + p.y, 0) / count};
  const inaccuracy = Math.hypot(mean.x, mean.y);
  const imprecision = Math.sqrt(points.reduce((s, p) => s + (p.x - mean.x) ** 2 + (p.y - mean.y) ** 2, 0) / count);
  return {points, mean, inaccuracy, imprecision};
}

// --- Semana 2: serie de Taylor --------------------------------------------------------
const factorial = n => { let value = 1; for (let k = 2; k <= n; k++) value *= k; return value; };
/** Derivadas k-ésimas en a de las funciones del laboratorio. */
export const TAYLOR_FUNCTIONS = {
  exp: {label: 'eˣ', f: Math.exp, derivative: (k, a) => Math.exp(a)},
  sin: {label: 'sen(x)', f: Math.sin, derivative: (k, a) => [Math.sin(a), Math.cos(a), -Math.sin(a), -Math.cos(a)][k % 4]},
  cos: {label: 'cos(x)', f: Math.cos, derivative: (k, a) => [Math.cos(a), -Math.sin(a), -Math.cos(a), Math.sin(a)][k % 4]},
  ln: {label: 'ln(1 + x)', f: x => Math.log(1 + x), domain: x => x > -1,
       derivative: (k, a) => k === 0 ? Math.log(1 + a) : (k % 2 ? 1 : -1) * factorial(k - 1) / (1 + a) ** k},
};
export function taylor(key, a, x, order) {
  const fn = TAYLOR_FUNCTIONS[key];
  if (!fn) throw new NumericError('Función no disponible.');
  if (fn.domain && !(fn.domain(a) && fn.domain(x))) throw new NumericError('ln(1 + x) solo está definida para x > −1.');
  const exact = fn.f(x);
  const terms = [];
  let sum = 0;
  for (let k = 0; k <= order; k++) {
    const term = fn.derivative(k, a) / factorial(k) * (x - a) ** k;
    sum += term;
    terms.push({k, term, sum, error: Math.abs(exact - sum),
                relative: exact !== 0 ? Math.abs((exact - sum) / exact) : null});
  }
  const polynomial = value => {
    let total = 0;
    for (let k = 0; k <= order; k++) total += fn.derivative(k, a) / factorial(k) * (value - a) ** k;
    return total;
  };
  return {exact, approximation: sum, error: Math.abs(exact - sum), terms, polynomial, f: fn.f};
}

// --- Semana 5: raíces de polinomios ---------------------------------------------------
/** Coeficientes de mayor a menor grado. Devuelve el cociente por (x − r) y el residuo p(r). */
export function horner(coefficients, r) {
  const quotient = [coefficients[0]];
  for (let i = 1; i < coefficients.length; i++) quotient.push(coefficients[i] + quotient[i - 1] * r);
  const remainder = quotient.pop();
  return {quotient, remainder};
}
export const polyval = (coefficients, x) => coefficients.reduce((total, c) => total * x + c, 0);
/** Newton con división sintética doble (Birge-Vieta). */
export function birgeVieta(coefficients, x0, tolerance = 1e-8, maxIterations = 50) {
  const iterations = [];
  let x = x0;
  for (let n = 0; n < maxIterations; n++) {
    const first = horner(coefficients, x);
    const second = horner(first.quotient, x);
    if (Math.abs(second.remainder) < EPS) throw new NumericError(`p′(x) se anula en x = ${fmt(x)}: elige otro valor inicial.`);
    const next = x - first.remainder / second.remainder;
    iterations.push({n, x, p: first.remainder, dp: second.remainder, next, step: Math.abs(next - x)});
    if (Math.abs(next - x) <= tolerance) return {root: next, iterations, converged: true};
    x = next;
  }
  return {root: x, iterations, converged: false};
}
/** Todas las raíces reales por Birge-Vieta + deflación. Lo que no se pudo factorizar queda en `remaining`. */
export function polynomialRoots(coefficients, x0 = 0, tolerance = 1e-10) {
  let current = coefficients.slice();
  while (current.length > 1 && current[0] === 0) current.shift();
  if (current.length < 2) throw new NumericError('Escribe al menos dos coeficientes y un coeficiente principal distinto de cero.');
  const roots = [], stages = [];
  while (current.length > 2) {
    let found = null;
    for (const start of [x0, x0 + 1, x0 - 1, x0 + 3, x0 - 3, 0.5, -0.5, 10, -10]) {
      try {
        const attempt = birgeVieta(current, start, tolerance, 80);
        if (attempt.converged && Number.isFinite(attempt.root)) { found = {...attempt, start}; break; }
      } catch { /* se prueba el siguiente inicio */ }
    }
    if (!found) break;
    const {quotient} = horner(current, found.root);
    stages.push({polynomial: current, root: found.root, start: found.start, iterations: found.iterations, quotient});
    roots.push(found.root);
    current = quotient;
  }
  if (current.length === 2) { roots.push(-current[1] / current[0]); current = [current[0]]; }
  return {roots, stages, remaining: current};
}
/** Müller con aritmética real: se detiene si la parábola no corta el eje real. */
export function muller(f, x0, x1, x2, tolerance = 1e-8, maxIterations = 50) {
  const iterations = [];
  for (let n = 0; n < maxIterations; n++) {
    const h0 = x1 - x0, h1 = x2 - x1;
    const d0 = (f(x1) - f(x0)) / h0, d1 = (f(x2) - f(x1)) / h1;
    const a = (d1 - d0) / (h1 + h0), b = a * h1 + d1, c = f(x2);
    const discriminant = b * b - 4 * a * c;
    if (discriminant < 0) return {root: null, iterations, converged: false, complex: true};
    const root = Math.sqrt(discriminant);
    const denominator = Math.abs(b + root) > Math.abs(b - root) ? b + root : b - root;
    if (Math.abs(denominator) < EPS) throw new NumericError('Los tres puntos no definen una parábola útil: cambia los valores iniciales.');
    const next = x2 - 2 * c / denominator;
    iterations.push({n, x0, x1, x2, next, step: Math.abs(next - x2), f: f(next)});
    if (Math.abs(next - x2) <= tolerance) return {root: next, iterations, converged: true};
    x0 = x1; x1 = x2; x2 = next;
  }
  return {root: x2, iterations, converged: false};
}

// --- Semana 6: métodos directos ---------------------------------------------------------
function checkSquare(matrix, vector) {
  const n = matrix.length;
  if (!n || matrix.some(row => row.length !== n)) throw new NumericError('La matriz debe ser cuadrada (mismo número de filas y columnas).');
  if (vector && vector.length !== n) throw new NumericError('El vector b debe tener un valor por fila.');
  return n;
}
/** Gauss-Jordan con pivoteo parcial sobre [A | B]. Registra cada operación de fila. */
export function gaussJordan(matrix, right) {
  const n = checkSquare(matrix);
  const augmented = matrix.map((row, i) => [...row, ...right[i]]);
  const steps = [{label: 'Matriz aumentada inicial', matrix: clone(augmented)}];
  for (let column = 0; column < n; column++) {
    let pivot = column;
    for (let row = column + 1; row < n; row++) if (Math.abs(augmented[row][column]) > Math.abs(augmented[pivot][column])) pivot = row;
    if (Math.abs(augmented[pivot][column]) < EPS) throw new NumericError(`La matriz es singular: no hay pivote distinto de cero en la columna ${column + 1}.`);
    if (pivot !== column) {
      [augmented[pivot], augmented[column]] = [augmented[column], augmented[pivot]];
      steps.push({label: `Intercambio F${column + 1} ↔ F${pivot + 1} (pivoteo parcial)`, matrix: clone(augmented)});
    }
    const value = augmented[column][column];
    if (Math.abs(value - 1) > EPS) {
      augmented[column] = augmented[column].map(entry => entry / value);
      steps.push({label: `F${column + 1} ← F${column + 1} / ${fmt(value)}`, matrix: clone(augmented)});
    }
    const operations = [];
    for (let row = 0; row < n; row++) {
      const factor = augmented[row][column];
      if (row === column || Math.abs(factor) < EPS) continue;
      augmented[row] = augmented[row].map((entry, j) => entry - factor * augmented[column][j]);
      operations.push(`F${row + 1} ← F${row + 1} − (${fmt(factor)})·F${column + 1}`);
    }
    if (operations.length) steps.push({label: operations.join(';  '), matrix: clone(augmented)});
  }
  return {result: augmented.map(row => row.slice(n)), steps};
}
export const identity = n => Array.from({length: n}, (_, i) => Array.from({length: n}, (_, j) => +(i === j)));
export const inverse = matrix => gaussJordan(matrix, identity(matrix.length));
export const matVec = (matrix, vector) => matrix.map(row => row.reduce((total, value, j) => total + value * vector[j], 0));
export const matMul = (a, b) => a.map(row => b[0].map((_, j) => row.reduce((total, value, k) => total + value * b[k][j], 0)));
export const normInf = vector => Math.max(...vector.map(Math.abs));
export const residual = (matrix, x, b) => normInf(matVec(matrix, x).map((value, i) => b[i] - value));
/** Descomposición de Doolittle PA = LU con pivoteo parcial, y solución de Ax = b. */
export function luDecomposition(matrix, vector = null) {
  const n = checkSquare(matrix, vector);
  const upper = clone(matrix), lower = identity(n), permutation = Array.from({length: n}, (_, i) => i);
  const steps = [];
  for (let column = 0; column < n - 1; column++) {
    let pivot = column;
    for (let row = column + 1; row < n; row++) if (Math.abs(upper[row][column]) > Math.abs(upper[pivot][column])) pivot = row;
    if (Math.abs(upper[pivot][column]) < EPS) throw new NumericError('La matriz es singular: no admite una descomposición LU utilizable.');
    if (pivot !== column) {
      [upper[pivot], upper[column]] = [upper[column], upper[pivot]];
      [permutation[pivot], permutation[column]] = [permutation[column], permutation[pivot]];
      for (let j = 0; j < column; j++) [lower[pivot][j], lower[column][j]] = [lower[column][j], lower[pivot][j]];
      steps.push(`Intercambio F${column + 1} ↔ F${pivot + 1} (pivoteo parcial).`);
    }
    for (let row = column + 1; row < n; row++) {
      const factor = upper[row][column] / upper[column][column];
      lower[row][column] = factor;
      for (let j = column; j < n; j++) upper[row][j] -= factor * upper[column][j];
      upper[row][column] = 0;
      steps.push(`l${row + 1}${column + 1} = ${fmt(factor)}: F${row + 1} ← F${row + 1} − (${fmt(factor)})·F${column + 1}.`);
    }
  }
  if (Math.abs(upper[n - 1][n - 1]) < EPS) throw new NumericError('La matriz es singular: U tiene un cero en la diagonal.');
  const swaps = permutation.reduce((count, value, i, list) => count + list.slice(i + 1).filter(other => other < value).length, 0);
  const output = {lower, upper, permutation, steps,
                  determinant: (swaps % 2 ? -1 : 1) * upper.reduce((product, row, i) => product * row[i], 1)};
  if (vector) {
    const pb = permutation.map(i => vector[i]);
    const d = [];
    for (let i = 0; i < n; i++) d[i] = pb[i] - lower[i].slice(0, i).reduce((total, value, j) => total + value * d[j], 0);
    const x = [];
    for (let i = n - 1; i >= 0; i--) x[i] = (d[i] - upper[i].slice(i + 1).reduce((total, value, j) => total + value * x[i + 1 + j], 0)) / upper[i][i];
    Object.assign(output, {pb, d, solution: x});
  }
  return output;
}
const solve = (matrix, vector) => luDecomposition(matrix, vector).solution;

// --- Semana 7: métodos iterativos y matrices especiales ---------------------------------
export function diagonalDominance(matrix) {
  const rows = matrix.map((row, i) => {
    const off = row.reduce((total, value, j) => total + (j === i ? 0 : Math.abs(value)), 0);
    return {diagonal: Math.abs(row[i]), off, strict: Math.abs(row[i]) > off};
  });
  return {rows, strict: rows.every(row => row.strict)};
}
/** Jacobi (`seidel: false`) o Gauss-Seidel; con `relaxation ≠ 1`, sobrerrelajación (SOR). */
export function iterate(matrix, vector, {seidel = true, relaxation = 1, tolerance = 1e-6, maxIterations = 100} = {}) {
  const n = checkSquare(matrix, vector);
  if (matrix.some((row, i) => Math.abs(row[i]) < EPS)) throw new NumericError('Hay un cero en la diagonal: reordena las ecuaciones antes de iterar.');
  let x = new Array(n).fill(0);
  const iterations = [{k: 0, x: x.slice(), step: null, residual: residual(matrix, x, vector)}];
  for (let k = 1; k <= maxIterations; k++) {
    const previous = x.slice();
    const next = x.slice();
    for (let i = 0; i < n; i++) {
      let total = vector[i];
      for (let j = 0; j < n; j++) if (j !== i) total -= matrix[i][j] * (seidel ? next[j] : previous[j]);
      const value = total / matrix[i][i];
      next[i] = seidel ? relaxation * value + (1 - relaxation) * previous[i] : value;
    }
    x = next;
    const step = normInf(x.map((value, i) => value - previous[i]));
    const record = {k, x: x.slice(), step, residual: residual(matrix, x, vector)};
    iterations.push(record);
    if (!x.every(Number.isFinite) || record.residual > 1e12) return {solution: x, iterations, converged: false, diverged: true};
    if (step <= tolerance) return {solution: x, iterations, converged: true, diverged: false};
  }
  return {solution: x, iterations, converged: false, diverged: false};
}
/** Algoritmo de Thomas para sistemas tridiagonales (a: subdiagonal, b: diagonal, c: superdiagonal). */
export function thomas(a, b, c, d) {
  const n = b.length, cp = [], dp = [];
  for (let i = 0; i < n; i++) {
    const denominator = b[i] - (i ? a[i] * cp[i - 1] : 0);
    if (Math.abs(denominator) < EPS) throw new NumericError('Pivote nulo en el algoritmo de Thomas.');
    cp[i] = i < n - 1 ? c[i] / denominator : 0;
    dp[i] = (d[i] - (i ? a[i] * dp[i - 1] : 0)) / denominator;
  }
  const x = new Array(n);
  x[n - 1] = dp[n - 1];
  for (let i = n - 2; i >= 0; i--) x[i] = dp[i] - cp[i] * x[i + 1];
  return x;
}

// --- Semana 8: regresión por mínimos cuadrados -------------------------------------------
function checkPoints(points, minimum = 2) {
  if (points.length < minimum) throw new NumericError(`Se necesitan al menos ${minimum} puntos.`);
}
function fitQuality(points, predict, parameters) {
  const mean = points.reduce((total, [, y]) => total + y, 0) / points.length;
  const st = points.reduce((total, [, y]) => total + (y - mean) ** 2, 0);
  const sr = points.reduce((total, [x, y]) => total + (y - predict(x)) ** 2, 0);
  return {st, sr, r2: st > 0 ? 1 - sr / st : 1,
          standardError: points.length > parameters ? Math.sqrt(sr / (points.length - parameters)) : 0};
}
/** Ajuste polinomial de grado m por ecuaciones normales. Coeficientes a0, a1, …, am. */
export function polynomialFit(points, degree = 1) {
  checkPoints(points, degree + 1);
  const size = degree + 1;
  const normal = Array.from({length: size}, (_, i) => Array.from({length: size}, (_, j) => points.reduce((total, [x]) => total + x ** (i + j), 0)));
  const right = Array.from({length: size}, (_, i) => points.reduce((total, [x, y]) => total + y * x ** i, 0));
  let coefficients;
  try { coefficients = solve(normal, right); }
  catch { throw new NumericError('Los valores de x no permiten ese ajuste: hacen falta más abscisas distintas.'); }
  const predict = x => coefficients.reduce((total, c, k) => total + c * x ** k, 0);
  return {coefficients, predict, normal, right, ...fitQuality(points, predict, size)};
}
/** Modelos linealizables: exponencial y = a·e^(bx) y potencia y = a·x^b. La calidad se mide en los datos originales. */
export function transformedFit(points, model) {
  checkPoints(points);
  if (points.some(([, y]) => y <= 0)) throw new NumericError('Este modelo requiere y > 0 en todos los puntos (se usa ln y).');
  if (model === 'power' && points.some(([x]) => x <= 0)) throw new NumericError('El modelo de potencia requiere x > 0 en todos los puntos (se usa ln x).');
  const transformed = points.map(([x, y]) => [model === 'power' ? Math.log(x) : x, Math.log(y)]);
  const line = polynomialFit(transformed, 1);
  const a = Math.exp(line.coefficients[0]), b = line.coefficients[1];
  const predict = model === 'power' ? x => a * x ** b : x => a * Math.exp(b * x);
  return {a, b, predict, coefficients: [a, b], ...fitQuality(points, predict, 2)};
}

// --- Semanas 9 y 10: interpolación --------------------------------------------------------
function checkDistinct(points) {
  checkPoints(points);
  const seen = new Set();
  for (const [x] of points) {
    if (seen.has(x)) throw new NumericError(`El valor x = ${x} está repetido: cada abscisa debe ser distinta.`);
    seen.add(x);
  }
}
/** Tabla triangular de diferencias divididas: table[j][i] = f[x_i, …, x_{i+j}]. */
export function dividedDifferences(points) {
  checkDistinct(points);
  const table = [points.map(([, y]) => y)];
  for (let j = 1; j < points.length; j++) {
    table.push(table[j - 1].slice(0, -1).map((value, i) => (table[j - 1][i + 1] - value) / (points[i + j][0] - points[i][0])));
  }
  const coefficients = table.map(column => column[0]);
  const evaluate = x => {
    let total = coefficients[coefficients.length - 1];
    for (let k = coefficients.length - 2; k >= 0; k--) total = total * (x - points[k][0]) + coefficients[k];
    return total;
  };
  return {table, coefficients, evaluate};
}
/** Diferencias finitas hacia adelante (solo tienen sentido con paso constante). */
export function forwardDifferences(points) {
  const h = points[1][0] - points[0][0];
  const uniform = points.every(([x], i) => i === 0 || Math.abs(x - points[i - 1][0] - h) < 1e-9 * Math.max(1, Math.abs(h)));
  const table = [points.map(([, y]) => y)];
  for (let j = 1; j < points.length; j++) table.push(table[j - 1].slice(0, -1).map((value, i) => table[j - 1][i + 1] - value));
  return {h, uniform, table};
}
/** Coeficientes de la forma de potencias a0 + a1·x + … resolviendo el sistema de Vandermonde. */
export function vandermonde(points) {
  checkDistinct(points);
  const matrix = points.map(([x]) => points.map((_, k) => x ** k));
  return {matrix, coefficients: solve(matrix, points.map(([, y]) => y))};
}
export function lagrange(points, x) {
  checkDistinct(points);
  const basis = points.map(([xi], i) => points.reduce((product, [xj], j) => j === i ? product : product * (x - xj) / (xi - xj), 1));
  return {basis, value: basis.reduce((total, l, i) => total + l * points[i][1], 0)};
}
/** Spline cúbico natural (S″ = 0 en los extremos). Devuelve los coeficientes por tramo. */
export function naturalSpline(points) {
  checkDistinct(points);
  const sorted = points.slice().sort((p, q) => p[0] - q[0]);
  const n = sorted.length - 1;
  const h = Array.from({length: n}, (_, i) => sorted[i + 1][0] - sorted[i][0]);
  let second = new Array(n + 1).fill(0);
  if (n > 1) {
    const a = [], b = [], c = [], d = [];
    for (let i = 1; i < n; i++) {
      a.push(i === 1 ? 0 : h[i - 1]);
      b.push(2 * (h[i - 1] + h[i]));
      c.push(i === n - 1 ? 0 : h[i]);
      d.push(6 * ((sorted[i + 1][1] - sorted[i][1]) / h[i] - (sorted[i][1] - sorted[i - 1][1]) / h[i - 1]));
    }
    second = [0, ...thomas(a, b, c, d), 0];
  }
  const segments = h.map((width, i) => ({
    x0: sorted[i][0], x1: sorted[i + 1][0], a: sorted[i][1],
    b: (sorted[i + 1][1] - sorted[i][1]) / width - width * (2 * second[i] + second[i + 1]) / 6,
    c: second[i] / 2, d: (second[i + 1] - second[i]) / (6 * width),
  }));
  const evaluate = x => {
    const segment = segments.find(s => x <= s.x1) || segments[segments.length - 1];
    const t = x - segment.x0;
    return segment.a + segment.b * t + segment.c * t * t + segment.d * t ** 3;
  };
  return {points: sorted, second, segments, evaluate};
}
export function linearSpline(points) {
  const sorted = points.slice().sort((p, q) => p[0] - q[0]);
  return x => {
    let i = sorted.findIndex(([value]) => x <= value);
    if (i === -1) i = sorted.length - 1;
    if (i === 0) i = 1;
    const [x0, y0] = sorted[i - 1], [x1, y1] = sorted[i];
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0);
  };
}

// --- Semana 11: aproximación de Fourier ------------------------------------------------------
const wrap = t => ((t + Math.PI) % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI) - Math.PI;
export const WAVES = {
  square: {label: 'Onda cuadrada', f: t => (wrap(t) >= 0 ? 1 : -1)},
  sawtooth: {label: 'Diente de sierra', f: t => wrap(t) / Math.PI},
  triangle: {label: 'Onda triangular', f: t => 1 - 2 * Math.abs(wrap(t)) / Math.PI},
  rectified: {label: 'Seno rectificado |sen t|', f: t => Math.abs(Math.sin(t))},
};
/** Coeficientes de Fourier en [−π, π] por integración numérica (regla del punto medio, m subintervalos). */
export function fourierCoefficients(f, harmonics, m = 2048) {
  const h = 2 * Math.PI / m;
  const samples = Array.from({length: m}, (_, i) => -Math.PI + (i + 0.5) * h);
  const values = samples.map(f);
  const integral = weight => samples.reduce((total, t, i) => total + values[i] * weight(t), 0) * h;
  const clean = value => Math.abs(value) < 1e-6 ? 0 : value;
  const a0 = clean(integral(() => 1) / (2 * Math.PI));
  const a = [], b = [];
  for (let k = 1; k <= harmonics; k++) {
    a.push(clean(integral(t => Math.cos(k * t)) / Math.PI));
    b.push(clean(integral(t => Math.sin(k * t)) / Math.PI));
  }
  const series = t => a0 + a.reduce((total, ak, i) => total + ak * Math.cos((i + 1) * t) + b[i] * Math.sin((i + 1) * t), 0);
  const rms = Math.sqrt(samples.reduce((total, t, i) => total + (values[i] - series(t)) ** 2, 0) / m);
  return {a0, a, b, series, rms};
}

// --- Semana 12: integración numérica ----------------------------------------------------------
function sample(f, a, b, n) {
  const x = linspace(a, b, n + 1), y = x.map(f);
  if (y.some(value => !Number.isFinite(value))) throw new NumericError('La función no está definida en algún punto del intervalo.');
  return {h: (b - a) / n, x, y};
}
export function trapezoid(f, a, b, n) {
  const {h, x, y} = sample(f, a, b, n);
  return {h, x, y, value: h * (y[0] / 2 + y.slice(1, -1).reduce((total, v) => total + v, 0) + y[n] / 2)};
}
export function simpson13(f, a, b, n) {
  if (n % 2) throw new NumericError('Simpson 1/3 necesita un número par de subintervalos.');
  const {h, x, y} = sample(f, a, b, n);
  let total = y[0] + y[n];
  for (let i = 1; i < n; i++) total += (i % 2 ? 4 : 2) * y[i];
  return {h, x, y, value: h / 3 * total};
}
export function simpson38(f, a, b, n) {
  if (n % 3) throw new NumericError('Simpson 3/8 necesita un número de subintervalos múltiplo de 3.');
  const {h, x, y} = sample(f, a, b, n);
  let total = y[0] + y[n];
  for (let i = 1; i < n; i++) total += (i % 3 ? 3 : 2) * y[i];
  return {h, x, y, value: 3 * h / 8 * total};
}
/** Tabla de Romberg: R[i][0] es el trapecio con 2^i subintervalos; cada columna elimina un orden del error. */
export function romberg(f, a, b, levels = 5) {
  const table = [];
  for (let i = 0; i < levels; i++) {
    const row = [trapezoid(f, a, b, 2 ** i).value];
    for (let k = 1; k <= i; k++) row.push((4 ** k * row[k - 1] - table[i - 1][k - 1]) / (4 ** k - 1));
    table.push(row);
  }
  const last = table[levels - 1];
  return {table, value: last[last.length - 1], estimate: levels > 1 ? Math.abs(last[last.length - 1] - last[last.length - 2]) : null};
}
/** Integral doble en un rectángulo con Simpson 1/3 compuesto en ambas direcciones. */
export function doubleSimpson(f, ax, bx, ay, by, nx, ny) {
  return simpson13(x => simpson13(y => f(x, y), ay, by, ny).value, ax, bx, nx).value;
}
/** Referencia de alta precisión para medir el error real de las reglas. */
export const referenceIntegral = (f, a, b) => romberg(f, a, b, 12).value;

// --- Semana 13: derivación numérica -------------------------------------------------------------
export const DIFFERENCE_FORMULAS = [
  {key: 'forward', label: 'Hacia adelante (2 puntos)', order: 1, d: (f, x, h) => (f(x + h) - f(x)) / h},
  {key: 'backward', label: 'Hacia atrás (2 puntos)', order: 1, d: (f, x, h) => (f(x) - f(x - h)) / h},
  {key: 'central', label: 'Centrada (2 puntos)', order: 2, d: (f, x, h) => (f(x + h) - f(x - h)) / (2 * h)},
  {key: 'forward3', label: 'Hacia adelante (3 puntos)', order: 2, d: (f, x, h) => (-f(x + 2 * h) + 4 * f(x + h) - 3 * f(x)) / (2 * h)},
  {key: 'central4', label: 'Centrada (4 puntos)', order: 4, d: (f, x, h) => (-f(x + 2 * h) + 8 * f(x + h) - 8 * f(x - h) + f(x - 2 * h)) / (12 * h)},
];
export const secondDerivative = (f, x, h) => (f(x + h) - 2 * f(x) + f(x - h)) / (h * h);
export const thirdDerivative = (f, x, h) => (f(x + 2 * h) - 2 * f(x + h) + 2 * f(x - h) - f(x - 2 * h)) / (2 * h ** 3);
/** Extrapolación de Richardson sobre la diferencia centrada. */
export function richardson(f, x, h, levels = 4) {
  const central = DIFFERENCE_FORMULAS[2].d;
  const table = [];
  for (let i = 0; i < levels; i++) {
    const row = [central(f, x, h / 2 ** i)];
    for (let k = 1; k <= i; k++) row.push((4 ** k * row[k - 1] - table[i - 1][k - 1]) / (4 ** k - 1));
    table.push(row);
  }
  return {table, value: table[levels - 1][levels - 1]};
}
export const referenceDerivative = (f, x) => richardson(f, x, 0.05 * Math.max(1, Math.abs(x)), 5).value;

// --- Semanas 14 y 15: ecuaciones diferenciales ordinarias ---------------------------------------
export const ODE_METHODS = {
  euler: {label: 'Euler', order: 1, step: (f, t, y, h) => y + h * f(t, y)},
  heun: {label: 'Euler modificado (Heun)', order: 2, step: (f, t, y, h) => {
    const k1 = f(t, y), k2 = f(t + h, y + h * k1);
    return y + h * (k1 + k2) / 2;
  }},
  midpoint: {label: 'Punto medio (RK2)', order: 2, step: (f, t, y, h) => y + h * f(t + h / 2, y + h / 2 * f(t, y))},
  ralston: {label: 'Ralston (RK2)', order: 2, step: (f, t, y, h) => {
    const k1 = f(t, y), k2 = f(t + 3 * h / 4, y + 3 * h / 4 * k1);
    return y + h * (k1 / 3 + 2 * k2 / 3);
  }},
  rk3: {label: 'Runge-Kutta 3', order: 3, step: (f, t, y, h) => {
    const k1 = f(t, y), k2 = f(t + h / 2, y + h / 2 * k1), k3 = f(t + h, y - h * k1 + 2 * h * k2);
    return y + h * (k1 + 4 * k2 + k3) / 6;
  }},
  rk4: {label: 'Runge-Kutta 4', order: 4, step: (f, t, y, h) => rk4Stages(f, t, y, h).next},
};
/** Las cuatro pendientes de un paso de RK4, para mostrar el desarrollo. */
export function rk4Stages(f, t, y, h) {
  const k1 = f(t, y), k2 = f(t + h / 2, y + h / 2 * k1), k3 = f(t + h / 2, y + h / 2 * k2), k4 = f(t + h, y + h * k3);
  return {k1, k2, k3, k4, next: y + h * (k1 + 2 * k2 + 2 * k3 + k4) / 6};
}
export function solveOde(f, t0, y0, h, steps, method = 'euler') {
  const {step} = ODE_METHODS[method];
  const t = [t0], y = [y0];
  for (let i = 0; i < steps; i++) {
    const next = step(f, t[i], y[i], h);
    if (!Number.isFinite(next)) throw new NumericError(`La solución deja de ser finita cerca de t = ${fmt(t[i] + h)}: reduce el paso h o revisa la función.`);
    t.push(t0 + (i + 1) * h);
    y.push(next);
  }
  return {t, y};
}
/** Referencia: RK4 con 64 subpasos por paso. */
export function referenceOde(f, t0, y0, h, steps) {
  const fine = solveOde(f, t0, y0, h / 64, steps * 64, 'rk4');
  return {t: fine.t.filter((_, i) => i % 64 === 0), y: fine.y.filter((_, i) => i % 64 === 0), dense: fine};
}

// --- Semana 16: ecuaciones en derivadas parciales -------------------------------------------------
/** Ecuación de calor u_t = α·u_xx con el esquema explícito. Estable si λ = α·Δt/Δx² ≤ 1/2. */
export function heatExplicit({nodes = 11, lambda = 0.4, steps = 40, left = 0, right = 0, initial = x => Math.sin(Math.PI * x)} = {}) {
  const x = linspace(0, 1, nodes);
  let u = x.map(initial);
  u[0] = left; u[nodes - 1] = right;
  const history = [u.slice()];
  for (let step = 0; step < steps; step++) {
    const next = u.slice();
    for (let i = 1; i < nodes - 1; i++) next[i] = u[i] + lambda * (u[i + 1] - 2 * u[i] + u[i - 1]);
    u = next;
    history.push(u.slice());
  }
  const peak = Math.max(...u.map(Math.abs));
  const start = Math.max(...history[0].map(Math.abs));
  return {x, history, lambda, stable: lambda <= 0.5 + 1e-12, grew: peak > start * 1.0001};
}
/** Ecuación de Laplace en una placa con el método de Liebmann (Gauss-Seidel con sobrerrelajación). */
export function laplacePlate({size = 12, top = 100, bottom = 0, left = 75, right = 50, relaxation = 1.5, tolerance = 1e-6, maxIterations = 2000} = {}) {
  const grid = Array.from({length: size}, () => new Array(size).fill((top + bottom + left + right) / 4));
  for (let i = 0; i < size; i++) { grid[0][i] = bottom; grid[size - 1][i] = top; grid[i][0] = left; grid[i][size - 1] = right; }
  grid[0][0] = (bottom + left) / 2; grid[0][size - 1] = (bottom + right) / 2;
  grid[size - 1][0] = (top + left) / 2; grid[size - 1][size - 1] = (top + right) / 2;
  const changes = [];
  for (let iteration = 1; iteration <= maxIterations; iteration++) {
    let change = 0;
    for (let i = 1; i < size - 1; i++) for (let j = 1; j < size - 1; j++) {
      const average = (grid[i + 1][j] + grid[i - 1][j] + grid[i][j + 1] + grid[i][j - 1]) / 4;
      const value = relaxation * average + (1 - relaxation) * grid[i][j];
      change = Math.max(change, Math.abs(value - grid[i][j]));
      grid[i][j] = value;
    }
    changes.push(change);
    if (!Number.isFinite(change) || change > 1e12) return {grid, changes, iterations: iteration, converged: false, diverged: true};
    if (change <= tolerance) return {grid, changes, iterations: iteration, converged: true, diverged: false};
  }
  return {grid, changes, iterations: maxIterations, converged: false, diverged: false};
}
