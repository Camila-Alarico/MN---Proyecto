const { test } = require("node:test");
const assert = require("node:assert/strict");
const { probarSistema } = require("../js/prueba.js");
const base = [[4, 1, 1], [1, 5, 1], [1, 1, 6]];

test("recibe el caso base sin mutarlo ni inventar una solución", () => {
  const A = base.map(fila => Object.freeze([...fila]));
  const b = Object.freeze([9, 14, 21]);
  const salida = probarSistema(Object.freeze(A), b);
  assert.equal(salida.estado, "valido");
  assert.deepEqual(salida.resultado, { dimension: 3, A: base, b: [9, 14, 21] });
  salida.resultado.A[0][0] = 99;
  salida.resultado.b[0] = 99;
  assert.equal(A[0][0], 4);
  assert.equal(b[0], 9);
});
test("acepta 2×2, cero, negativos, decimales y notación científica", () => {
  const salida = probarSistema([["0", "-2.5"], [" 1e-6 ", ".5"]], ["+3", "4."]);
  assert.deepEqual(salida.resultado, { dimension: 2, A: [[0, -2.5], [1e-6, .5]], b: [3, 4] });
});
test("rechaza vacíos en A y b sin convertirlos en cero", () => {
  for (const vacio of ["", "   "]) {
    assert.equal(probarSistema([[vacio, 1], [1, 2]], [3, 4]).campo, "a-0-0");
    assert.equal(probarSistema([[2, 1], [1, 2]], [3, vacio]).campo, "b-1");
  }
});
test("rechaza tipos y textos no numéricos, NaN, infinitos y desbordamiento", () => {
  for (const valor of [null, undefined, true, [], {}, "hola", "2abc", "0x10", "1,5", NaN, Infinity, -Infinity, "1e309"]) {
    for (const salida of [probarSistema([[valor, 1], [1, 2]], [3, 4]), probarSistema([[2, 1], [1, 2]], [valor, 4])]) {
      assert.equal(salida.estado, "invalido", String(valor));
      assert.equal(salida.resultado, null);
    }
  }
});
test("rechaza matriz irregular, tamaño fuera de alcance y vector incompatible", () => {
  for (const [A, b] of [[null, []], [[], []], [[[1]], [1]], [[[1, 2], [3]], [4, 5]], [base, [9, 14]], [base, null], [Array(2), [1, 2]], [[[1, 2], [3, 4]], Array(2)]]) {
    assert.equal(probarSistema(A, b).estado, "invalido");
  }
});
test("el resultado cambia con la entrada y no certifica solución única", () => {
  const salida = probarSistema([[1, 2], [2, 4]], [3, 6]);
  assert.equal(salida.estado, "valido");
  assert.deepEqual(salida.resultado.b, [3, 6]);
  assert.match(salida.mensaje, /No se ha calculado una solución/);
});
