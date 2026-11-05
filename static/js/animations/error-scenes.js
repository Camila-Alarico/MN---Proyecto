// Escenas del tema «Errores numéricos»: medidas de error sobre una recta numérica y
// amplificación de una perturbación al derivar numéricamente.
import {ns, ts, paren, sci, texSci, el} from './format.js';
import {svgEl, ticks} from './plot.js';

function readNumber(id, fallback) {
  const input = document.getElementById(id);
  if (!input || input.value.trim() === '') return fallback;
  const value = Number(input.value);
  return Number.isFinite(value) ? value : fallback;
}

// ---- Error absoluto, relativo, porcentual y tolerancia -----------------------------------------
function errorsScene() {
  const v = readNumber('true-value', 10), a = readNumber('approximate-value', 9.8);
  const tau = Math.abs(readNumber('error-tolerance', 0.1));
  const Ea = Math.abs(v - a), Er = v !== 0 ? Ea / Math.abs(v) : null, Ep = Er == null ? null : 100 * Er;
  const lo = Math.min(a, v - tau, v), hi = Math.max(a, v + tau, v);
  const half = Math.max((hi - lo) / 2, Math.abs(v) * 1e-6, 1e-9) * 1.35;
  const mid = (lo + hi) / 2;
  const LINE = 0.25, BRACKET = 0.62, BAR = -0.55;
  const pass = Ea <= tau;

  const base = p => {
    const y = p.Y(LINE);
    svgEl('line', {x1: p.left, x2: p.right, y1: y, y2: y, class: 'anim-numberline'}, p.grid);
    for (const value of ticks(p.x0, p.x1, 6)) {
      const x = p.X(value);
      svgEl('line', {x1: x, x2: x, y1: y - 6, y2: y + 6, class: 'anim-numberline'}, p.grid);
      svgEl('text', {x, y: y + 24, class: 'anim-tick', 'text-anchor': 'middle'}, p.grid).textContent = ns(value, 4);
    }
  };
  const bar = p => {
    const y = p.Y(BAR) - 11, width = p.right - p.left - 40, x = p.left + 20;
    return {x, y, width};
  };
  const frames = [
    {
      title: 'Ubicar el valor de referencia',
      text: `El valor de referencia es v = ${ns(v)}. Es el dato con el que se compara cualquier aproximación.`,
      tex: String.raw`v=${ts(v)}`, step: null, row: null,
      draw(p, {current}) {
        p.point(v, LINE, 'anim-point anim-point-root', current ? 7 : 6);
        p.label(v, LINE, `v = ${ns(v)}`, {dy: -14, dx: v >= a ? 4 : -4, anchor: v >= a ? 'start' : 'end', cls: 'anim-label anim-label-strong'});
      },
    },
    {
      title: 'Ubicar la aproximación',
      text: `La aproximación es ṽ = ${ns(a)}. Ahora medimos qué tan lejos quedó del valor de referencia.`,
      tex: String.raw`\tilde v=${ts(a)}`, step: null, row: null,
      draw(p, {current}) {
        p.point(a, LINE, 'anim-point anim-point-accent', current ? 7 : 6);
        p.label(a, LINE, `ṽ = ${ns(a)}`, {dy: -14, dx: v >= a ? -4 : 4, anchor: v >= a ? 'end' : 'start', cls: 'anim-label anim-label-strong'});
      },
    },
    {
      title: 'Error absoluto: la distancia',
      text: `Eₐ = |v − ṽ| = ${ns(Ea)}. Conserva las unidades del problema y nunca es negativo.`,
      tex: String.raw`E_a=|v-\tilde v|=|${ts(v)}-${paren(ts(a))}|=${ts(Ea)}`, step: null, row: null,
      draw(p) {
        const y = BRACKET;
        p.line(Math.min(v, a), y, Math.max(v, a), y, 'anim-line anim-bracket');
        p.line(v, y - 0.07, v, y + 0.07, 'anim-line anim-bracket');
        p.line(a, y - 0.07, a, y + 0.07, 'anim-line anim-bracket');
        p.label((v + a) / 2, y, `Eₐ = ${ns(Ea)}`, {dy: -10, cls: 'anim-label anim-label-strong'});
      },
    },
    {
      title: 'Error relativo: la proporción',
      text: Er == null
        ? 'Como v = 0, el error relativo no está definido: habría que dividir entre cero. En ese caso se informa solo el error absoluto.'
        : `Eᵣ = Eₐ/|v| = ${ns(Er, 8)}. La barra completa representa |v| = ${ns(Math.abs(v))}; la parte coloreada es la fracción que ocupa el error.`,
      tex: Er == null ? String.raw`E_r=\frac{E_a}{|v|}=\frac{${ts(Ea)}}{0}\;\text{no definido}` : String.raw`E_r=\frac{E_a}{|v|}=\frac{${ts(Ea)}}{${ts(Math.abs(v))}}=${ts(Er, 8)}`,
      step: null, row: null,
      draw(p, {current}) {
        const {x, y, width} = bar(p);
        p.raw('rect', {x, y, width, height: 22, rx: 6}, 'anim-bar-track anim-fade');
        if (Er == null) {
          p.raw('line', {x1: x, y1: y, x2: x + width, y2: y + 22}, 'anim-bar-cross');
          p.raw('text', {x: x + width / 2, y: y - 8, 'text-anchor': 'middle'}, 'anim-label anim-fade').textContent = 'Eᵣ no definido (v = 0)';
          return;
        }
        const fill = Math.max(3, Math.min(1, Er) * width);
        p.raw('rect', {x, y, width: fill, height: 22, rx: 6}, `anim-bar-fill ${current ? 'anim-grow' : ''}`);
        p.raw('text', {x, y: y - 8}, 'anim-label anim-fade').textContent = `|v| = ${ns(Math.abs(v))}`;
        p.raw('text', {x: x + width, y: y + 40, 'text-anchor': 'end'}, 'anim-label anim-fade').textContent = `Eᵣ = ${ns(Er, 8)} de |v|`;
      },
    },
    {
      title: 'Error porcentual',
      text: Ep == null ? 'Sin error relativo tampoco hay error porcentual.' : `Eₚ = 100·Eᵣ = ${ns(Ep, 6)} %. Es la misma proporción expresada en porcentaje.`,
      tex: Ep == null ? String.raw`E_p\;\text{no definido}` : String.raw`E_p=100\,E_r=100\,(${ts(Er, 8)})=${ts(Ep, 6)}\,\%`,
      step: null, row: null,
      draw(p) {
        if (Ep == null) return;
        const {x, y, width} = bar(p);
        p.raw('text', {x: x + Math.max(3, Math.min(1, Er) * width) + 10, y: y + 16}, 'anim-label anim-label-strong anim-fade').textContent = `${ns(Ep, 4)} %`;
      },
    },
    {
      title: pass ? 'Comparar con la tolerancia: cumple' : 'Comparar con la tolerancia: no cumple',
      text: `La zona permitida es [v − τ, v + τ] = [${ns(v - tau)}, ${ns(v + tau)}]. Como Eₐ = ${ns(Ea)} ${pass ? '≤' : '>'} τ = ${ns(tau)}, la aproximación ${pass ? 'se acepta' : 'no se acepta'}. La tolerancia es un umbral elegido; el error es una medida del resultado.`,
      tex: String.raw`E_a=${ts(Ea)}\;${pass ? '\\le' : '>'}\;\tau=${ts(tau)}`,
      step: null, row: null,
      draw(p, {current}) {
        if (!current) return;
        const y1 = p.Y(LINE + 0.22), y2 = p.Y(LINE - 0.22);
        p.raw('rect', {x: p.X(v - tau), y: y1, width: Math.max(2, p.X(v + tau) - p.X(v - tau)), height: y2 - y1, rx: 6}, 'anim-tolerance anim-fade');
        p.raw('text', {x: p.X(v + tau), y: y1 - 6, 'text-anchor': 'middle'}, 'anim-tick anim-fade').textContent = `v + τ`;
        p.raw('text', {x: p.X(v - tau), y: y1 - 6, 'text-anchor': 'middle'}, 'anim-tick anim-fade').textContent = `v − τ`;
        p.ring(a, LINE, pass ? 'anim-ring anim-ring-pass' : 'anim-ring anim-ring-fail', 14);
      },
    },
  ];
  return {
    title: `Errores de ṽ = ${ns(a)} frente a v = ${ns(v)}`,
    view: {x: [mid - half, mid + half], y: [-1, 1]}, pad: {l: 24, r: 24, t: 20, b: 20}, base, frames,
    figcaption: 'Usa los datos del explorador de esta página (al principio: v = 10, ṽ = 9.8, τ = 0.1). Cámbialos y pulsa Reiniciar.',
  };
}

// ---- Un paso menor puede dar un error mayor (derivada centrada con datos redondeados) -----------
function derivativeScene() {
  const r6 = x => Math.round(x * 1e6) / 1e6, exact = Math.E;
  const cases = [0.01, 0.0001].map(h => {
    const up = r6(Math.exp(1 + h)), down = r6(Math.exp(1 - h)), D = (up - down) / (2 * h);
    const pure = (Math.exp(1 + h) - Math.exp(1 - h)) / (2 * h);
    return {h, up, down, D, err: Math.abs(D - exact), trunc: Math.abs(pure - exact), noise: Math.abs(D - pure)};
  });
  const logWidth = value => Math.max(4, Math.min(100, (Math.log10(Math.max(value, 1e-9)) + 9) / 8 * 100));
  const card = (c, i, state) => {
    const shown = state >= i + 1, split = state >= 3;
    return el('article', {class: `anim-deriv-card${shown ? ' is-shown' : ''}${state === i + 1 ? ' is-changed' : ''}`}, [
      el('span', {class: 'eyebrow', text: `PASO h = ${ns(c.h, 6)}`}),
      el('dl', {}, [
        el('dt', {text: 'e^(1+h) con 6 decimales'}), el('dd', {text: shown ? c.up.toFixed(6) : '?'}),
        el('dt', {text: 'e^(1−h) con 6 decimales'}), el('dd', {text: shown ? c.down.toFixed(6) : '?'}),
        el('dt', {text: 'Dₕ'}), el('dd', {class: 'anim-deriv-value', text: shown ? ns(c.D, 6) : '?'}),
        el('dt', {text: '|Dₕ − e|'}), el('dd', {class: 'anim-deriv-error', text: shown ? sci(c.err, 2) : '?'}),
      ]),
      el('div', {class: 'anim-logbar', 'aria-hidden': 'true'}, [
        el('span', {class: 'anim-logbar-fill', style: `width:${shown ? logWidth(c.err) : 0}%`}),
      ]),
      split ? el('p', {class: 'anim-deriv-split', text: `Truncamiento ≈ ${sci(c.trunc, 1)} · redondeo amplificado ≈ ${sci(c.noise, 1)}`}) : null,
    ]);
  };
  const render = state => board => {
    board.append(
      el('p', {class: 'anim-deriv-exact', text: `Valor exacto: g′(1) = e ≈ ${exact.toFixed(6)}`}),
      el('div', {class: 'anim-deriv-grid'}, cases.map((c, i) => card(c, i, state))),
      el('p', {class: 'anim-deriv-scale', text: 'Barra en escala logarítmica: de 10⁻⁹ (izquierda) a 10⁻¹ (derecha).'}),
    );
  };
  const [a, b] = cases;
  return {
    kind: 'html', title: 'Derivada centrada de eᵗ en t = 1',
    frames: [
      {title: 'Plantear la fórmula', text: 'Se estima g′(1) con la diferencia centrada. Las muestras e^(1±h) solo se guardan con seis decimales: cada una lleva un error de redondeo de hasta 5·10⁻⁷.',
        tex: String.raw`D_h=\frac{e^{1+h}-e^{1-h}}{2h}`, render: render(0)},
      {title: `Con h = ${ns(a.h)}`, text: `Dₕ = (${a.up.toFixed(6)} − ${a.down.toFixed(6)})/${ns(2 * a.h)} = ${ns(a.D, 6)}. El error es ${sci(a.err, 2)}.`,
        tex: String.raw`D_{0.01}=\frac{${a.up.toFixed(6)}-${a.down.toFixed(6)}}{0.02}=${ts(a.D, 6)}`, render: render(1)},
      {title: `Con h = ${ns(b.h)} (un paso 100 veces menor)`, text: `Dₕ = (${b.up.toFixed(6)} − ${b.down.toFixed(6)})/${ns(2 * b.h)} = ${ns(b.D, 6)}. ¡El error sube a ${sci(b.err, 2)}!`,
        tex: String.raw`D_{0.0001}=\frac{${b.up.toFixed(6)}-${b.down.toFixed(6)}}{0.0002}=${ts(b.D, 6)}`, render: render(2)},
      {title: 'Por qué: se divide la perturbación entre 2h', text: `El truncamiento baja como h² (≈ ${sci(a.trunc, 1)} → ${sci(b.trunc, 1)}), pero el redondeo de los datos se divide entre 2h y crece como 1/h. Con h muy pequeño domina la perturbación amplificada.`,
        tex: String.raw`|D_h-e|\lesssim\underbrace{\tfrac{h^2}{6}e}_{\text{truncamiento}}+\underbrace{\tfrac{10^{-6}}{2h}}_{\text{redondeo}}\quad(${texSci(5e-7 / a.h, 0)}\;\text{vs}\;${texSci(5e-7 / b.h, 0)})`, render: render(3)},
    ],
  };
}

export const errorScenes = {errors: errorsScene, 'derivative-perturbation': derivativeScene};
