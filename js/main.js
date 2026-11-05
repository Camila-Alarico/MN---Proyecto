"use strict";

const CASO_BASE = { A: [[4, 1, 1], [1, 5, 1], [1, 1, 6]], b: [9, 14, 21] };
const formulario = document.getElementById("formulario");
const tamano = document.getElementById("tamano");
const matriz = document.getElementById("matriz");
const vector = document.getElementById("vector");
const estado = document.getElementById("estado");
const mensaje = document.getElementById("mensaje");
const resultado = document.getElementById("resultado");

function limpiarSalida(texto) {
  delete estado.dataset.estado;
  mensaje.textContent = texto;
  resultado.textContent = "";
  resultado.hidden = true;
  formulario.querySelectorAll('[aria-invalid="true"]').forEach(input => input.removeAttribute("aria-invalid"));
}

function crearCampo(id, nombre, valor) {
  const label = document.createElement("label");
  label.htmlFor = id;
  label.textContent = nombre;
  const input = document.createElement("input");
  input.id = id;
  input.name = id;
  input.type = "text";
  input.inputMode = "decimal";
  input.autocomplete = "off";
  input.spellcheck = false;
  input.required = true;
  input.setAttribute("aria-describedby", "ayuda mensaje");
  input.value = valor;
  label.append(input);
  return label;
}

function dibujarEntradas(n, datos = null) {
  matriz.replaceChildren();
  vector.replaceChildren();
  matriz.style.gridTemplateColumns = `repeat(${n}, minmax(0, 1fr))`;
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      matriz.append(crearCampo(`a-${i}-${j}`, `A(${i + 1}, ${j + 1})`, datos ? datos.A[i][j] : ""));
    }
    vector.append(crearCampo(`b-${i}`, `b(${i + 1})`, datos ? datos.b[i] : ""));
  }
}

function cargarCasoBase() {
  tamano.value = "3";
  dibujarEntradas(3, CASO_BASE);
  limpiarSalida("Caso base cargado. Pulsa «Probar datos» para comprobarlo.");
}

document.getElementById("caso-base").addEventListener("click", cargarCasoBase);
tamano.addEventListener("change", () => {
  dibujarEntradas(Number(tamano.value));
  limpiarSalida("Nuevo tamaño seleccionado. Completa A y b antes de probar.");
});
// Una salida anterior deja de ser válida cuando cambian los datos.
formulario.addEventListener("input", event => {
  if (event.target.tagName === "INPUT") limpiarSalida("Datos modificados. Pulsa «Probar datos» para volver a comprobarlos.");
});
formulario.addEventListener("submit", event => {
  event.preventDefault();
  limpiarSalida("");
  const n = Number(tamano.value);
  const A = Array.from({ length: n }, (_, i) =>
    Array.from({ length: n }, (_, j) => document.getElementById(`a-${i}-${j}`).value));
  const b = Array.from({ length: n }, (_, i) => document.getElementById(`b-${i}`).value);
  const salida = probarSistema(A, b);
  estado.dataset.estado = salida.estado;
  mensaje.textContent = salida.mensaje;
  if (salida.estado === "invalido") {
    const campo = document.getElementById(salida.campo);
    if (campo) {
      campo.setAttribute("aria-invalid", "true");
      campo.focus();
    }
    return;
  }
  const datos = salida.resultado;
  resultado.textContent = `A =\n${datos.A.map(fila => `[ ${fila.join(", ")} ]`).join("\n")}\n\nb = [ ${datos.b.join(", ")} ]`;
  resultado.hidden = false;
});

cargarCasoBase();
