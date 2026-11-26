// Los algoritmos del temario reproducen los ejercicios resueltos de las lecciones.
const {test} = require('node:test');
const assert = require('node:assert/strict');
const {pathToFileURL} = require('node:url');
const {resolve} = require('node:path');

const load = name => import(pathToFileURL(resolve(__dirname, '../static/js/temario', name)).href);
const six = value => value.toFixed(6);
const A = [[4, 1, 1], [1, 5, 1], [1, 1, 6]], b = [9, 14, 21];

test('el analizador de expresiones respeta precedencia y rechaza símbolos desconocidos', async () => {
  const {compile} = await load('expr.js');
  assert.equal(compile('2x^2 - 3(x+1)')(2), -1);
  assert.equal(compile('-x^2')(3), -9);
  assert.equal(compile('t*y', ['t', 'y'])(2, 3), 6);
  assert.throws(() => compile('foo(x)'));
  assert.throws(() => compile('2 +'));
});

test('Taylor, polinomios y sistemas lineales', async () => {
  const N = await load('numeric.js');
  assert.deepEqual(N.taylor('exp', 0, 1, 5).terms.map(t => six(t.sum)), ['1.000000', '2.000000', '2.500000', '2.666667', '2.708333', '2.716667']);
  assert.deepEqual(N.birgeVieta([1, -6, 11, -6], 0.5, 1e-6).iterations.slice(0, 3).map(it => six(it.next)), ['0.826087', '0.967693', '0.998544']);
  assert.deepEqual(N.polynomialRoots([1, -6, 11, -6], 0).roots.map(r => r.toFixed(6)).sort(), ['1.000000', '2.000000', '3.000000']);
  assert.deepEqual(N.gaussJordan(A, b.map(v => [v])).result.flat().map(six), ['1.000000', '2.000000', '3.000000']);
  assert.equal(six(N.inverse(A).result[0][0]), '0.271028');
  const lu = N.luDecomposition(A, b);
  assert.equal(six(lu.lower[2][1]), '0.157895');
  assert.equal(six(lu.upper[2][2]), '5.631579');
  assert.equal(lu.determinant.toFixed(4), '107.0000');
  assert.throws(() => N.gaussJordan([[1, 2], [2, 4]], [[3], [6]]));
  assert.equal(N.iterate(A, b, {seidel: false}).iterations.length - 1, 18);
  assert.equal(N.iterate(A, b).iterations.length - 1, 8);
});

test('ajuste de curvas, integración, derivación y ecuaciones diferenciales', async () => {
  const N = await load('numeric.js');
  const fit = N.polynomialFit([[1, 0.5], [2, 2.5], [3, 2], [4, 4], [5, 3.5], [6, 6], [7, 5.5]], 1);
  assert.deepEqual([...fit.coefficients, fit.r2].map(six), ['0.071429', '0.839286', '0.868318']);
  const points = [[1, 0], [4, 1.386294], [6, 1.791759], [5, 1.609438]];
  assert.equal(six(N.dividedDifferences(points).evaluate(2)), '0.628767');
  assert.equal(six(N.lagrange(points.slice(0, 3), 2).value), '0.565844');
  assert.equal(six(N.naturalSpline([[3, 2.5], [4.5, 1], [7, 2.5], [9, 0.5]]).evaluate(5)), '1.102890');
  assert.ok(Math.abs(N.fourierCoefficients(N.WAVES.square.f, 3).b[0] - 4 / Math.PI) < 1e-4);
  const g = x => 0.2 + 25 * x - 200 * x ** 2 + 675 * x ** 3 - 900 * x ** 4 + 400 * x ** 5;
  assert.deepEqual([N.trapezoid(g, 0, 0.8, 4).value, N.simpson13(g, 0, 0.8, 4).value, N.simpson38(g, 0, 0.8, 3).value, N.romberg(g, 0, 0.8, 3).value].map(six),
    ['1.484800', '1.623467', '1.519170', '1.640533']);
  const q = x => -0.1 * x ** 4 - 0.15 * x ** 3 - 0.5 * x ** 2 - 0.25 * x + 1.2;
  assert.equal(six(N.DIFFERENCE_FORMULAS[2].d(q, 0.5, 0.25)), '-0.934375');
  assert.equal(six(N.richardson(q, 0.5, 0.5, 2).value), '-0.912500');
  const f = (t, y) => 4 * Math.exp(0.8 * t) - 0.5 * y;
  assert.equal(six(N.solveOde(f, 0, 2, 1, 4, 'euler').y[4]), '56.849311');
  assert.equal(six(N.solveOde(f, 0, 2, 1, 4, 'heun').y[1]), '6.701082');
  assert.equal(six(N.solveOde(f, 0, 2, 1, 1, 'rk4').y[1]), '6.201037');
  assert.equal(N.laplacePlate({size: 5, relaxation: 1}).grid[2][2].toFixed(2), '56.25');
  assert.equal(N.heatExplicit({lambda: 0.4}).stable, true);
  assert.equal(N.heatExplicit({lambda: 0.6}).stable, false);
});
