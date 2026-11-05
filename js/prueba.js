"use strict";

// Función pura: no lee el DOM, no modifica las entradas y no resuelve Ax = b.
// Acepta números o textos decimales procedentes del formulario.
function probarSistema(A, b) {
  const fallo = (mensaje, campo = null) => ({ estado: "invalido", mensaje, campo, resultado: null });
  if (!Array.isArray(A) || ![2, 3].includes(A.length)) {
    return fallo("La matriz A debe tener 2 o 3 filas.");
  }
  const n = A.length;
  for (let i = 0; i < n; i++) {
    if (!Array.isArray(A[i]) || A[i].length !== n) {
      return fallo(`La matriz A debe ser cuadrada de ${n} × ${n}.`);
    }
  }
  if (!Array.isArray(b) || b.length !== n) {
    return fallo(`El vector b debe tener ${n} componentes, una por fila de A.`);
  }

  // Revisar el vacío ANTES de Number evita convertir accidentalmente "" en 0.
  const decimal = /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?$/i;
  function leerNumero(valor, nombre, campo) {
    if (typeof valor === "string" && valor.trim() === "") {
      return fallo(`Completa el campo ${nombre}.`, campo);
    }
    if (typeof valor !== "number" && (typeof valor !== "string" || !decimal.test(valor.trim()))) {
      return fallo(`${nombre} debe ser un número real; usa punto para los decimales.`, campo);
    }
    const numero = Number(valor);
    if (!Number.isFinite(numero)) {
      return fallo(`${nombre} debe ser finito y representable por el navegador.`, campo);
    }
    return numero;
  }

  const matriz = [];
  const vector = [];
  for (let i = 0; i < n; i++) {
    const fila = [];
    for (let j = 0; j < n; j++) {
      const valor = leerNumero(A[i][j], `A(${i + 1}, ${j + 1})`, `a-${i}-${j}`);
      if (typeof valor !== "number") return valor;
      fila.push(valor);
    }
    matriz.push(fila);
    const valor = leerNumero(b[i], `b(${i + 1})`, `b-${i}`);
    if (typeof valor !== "number") return valor;
    vector.push(valor);
  }
  return {
    estado: "valido",
    mensaje: `Datos aceptados: matriz ${n} × ${n} y vector de ${n} componentes. No se ha calculado una solución.`,
    campo: null,
    resultado: { dimension: n, A: matriz, b: vector }
  };
}

// Permite ejecutar las mismas comprobaciones con Node, sin paquetes adicionales.
if (typeof module !== "undefined" && module.exports) module.exports = { probarSistema };
