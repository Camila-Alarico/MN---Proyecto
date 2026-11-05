// Escenas de raíces de ecuaciones: bisección, regla falsa, Newton, secante, punto fijo y raíces
// múltiples. Los valores se calculan aquí mismo con la función del ejercicio resuelto, por lo que
// coinciden con la tabla (seis decimales) que acompaña a cada ejemplo.
import {n6, ns, t6, ts, sub, paren, texSci, sci} from './format.js';

export const f = x => x ** 3 - x - 2;
const df = x => 3 * x * x - 1;
export const ROOT = 1.5213797068045676;
const CUBIC_LEGEND = [['f(x) = x³ − x − 2', 'anim-curve']];
const cubicBase = p => {p.axes({yLabel: 'f(x)'}); p.curve(f);};
const slope = (x1, y1, x2, y2) => (y2 - y1) / (x2 - x1);

// ---- Bisección --------------------------------------------------------------------------------
export function bisectionIterations(fn, a, b, n) {
  const out = [];
  let A = a, B = b;
  for (let k = 1; k <= n; k++) {
    const c = (A + B) / 2, fc = fn(c), keepLeft = fn(A) * fc < 0;
    out.push({k, a: A, b: B, c, fc, na: keepLeft ? A : c, nb: keepLeft ? c : B});
    if (fc === 0) break;
    if (keepLeft) B = c; else A = c;
  }
  return out;
}
export function signFrame(a, b, {step = null} = {}) {
  const fa = f(a), fb = f(b);
  return {
    title: 'Comprobar el cambio de signo',
    text: `f(${ns(a)}) = ${ns(fa)} < 0 y f(${ns(b)}) = ${ns(fb)} > 0. Como f es continua, el teorema del valor intermedio asegura una raíz en [${ns(a)}, ${ns(b)}].`,
    tex: String.raw`f(${ts(a)})\,f(${ts(b)})=(${ts(fa)})(${ts(fb)})=${ts(fa * fb)}<0`,
    step, row: null,
    draw(p, {current}) {
      if (!current) return;
      p.band(a, b);
      p.point(a, fa, 'anim-point anim-point-neg');
      p.point(b, fb, 'anim-point anim-point-pos');
      p.label(a, fa, `f(${ns(a)}) = ${ns(fa)}`, {dy: 24});
      p.label(b, fb, `f(${ns(b)}) = ${ns(fb)}`, {dx: -10, dy: 5, anchor: 'end'});
    },
  };
}
export function bisectionFrame(it, {step = null, row = null} = {}) {
  const xs = `x${sub(it.k)}`;
  return {
    title: `Iteración ${it.k}: punto medio`,
    text: `${xs} = (${ns(it.a)} + ${ns(it.b)})/2 = ${ns(it.c)}. Como f(${xs}) = ${n6(it.fc)} ${it.fc < 0 ? '< 0' : '> 0'}, se conserva la mitad con cambio de signo: [${ns(it.na)}, ${ns(it.nb)}].`,
    tex: String.raw`x_{${it.k}}=\frac{${ts(it.a)}+${ts(it.b)}}{2}=${ts(it.c)},\qquad f(x_{${it.k}})=${t6(it.fc)}`,
    step, row,
    draw(p, {current}) {
      if (current) {
        p.band(it.a, it.b);
        p.band(it.na, it.nb, 'anim-band-keep');
        p.point(it.a, f(it.a), 'anim-point anim-point-muted', 4);
        p.point(it.b, f(it.b), 'anim-point anim-point-muted', 4);
        p.line(it.c, 0, it.c, it.fc, 'anim-line anim-dashed');
        p.point(it.c, it.fc, 'anim-point anim-point-accent');
        p.label(it.c, it.fc, `f(${xs}) = ${n6(it.fc)}`, {dy: it.fc < 0 ? 24 : -14});
      }
      p.point(it.c, 0, 'anim-point anim-point-axis', current ? 5.5 : 3.5);
      if (current || it.k <= 2) p.tag(it.c, xs);
    },
  };
}
function bisectionScene() {
  const its = bisectionIterations(f, 1, 2, 4), last = its[its.length - 1];
  const bound = (2 - 1) / 2 ** its.length;
  return {
    title: 'Bisección en [1, 2]', view: {x: [0.85, 2.15], y: [-2.8, 4.8]}, base: cubicBase, legend: CUBIC_LEGEND,
    frames: [
      signFrame(1, 2, {step: 0}),
      ...its.map(it => bisectionFrame(it, {step: it.k === 1 ? 1 : 2, row: it.k - 1})),
      {
        title: 'Acotar el error',
        text: `Tras ${its.length} pasos, |x${sub(its.length)} − r| ≤ (b − a)/2ⁿ = 1/16 = ${ns(bound)}. El error real, |${ns(last.c)} − ${n6(ROOT)}| = ${n6(Math.abs(last.c - ROOT))}, queda dentro de la cota.`,
        tex: String.raw`|x_{${its.length}}-r|\le\frac{b_0-a_0}{2^{${its.length}}}=\frac{1}{16}=${ts(bound)}`,
        step: 3, row: 3,
        draw(p, {current}) {
          if (!current) return;
          p.band(last.c - bound, last.c + bound, 'anim-band-keep');
          p.line(last.c - bound, 0, last.c + bound, 0, 'anim-line anim-bound');
          p.point(ROOT, 0, 'anim-point anim-point-root');
          p.ring(ROOT, 0);
          p.label(ROOT, 0, `r ≈ ${n6(ROOT)}`, {dy: -20});
        },
      },
    ],
  };
}

// ---- Regla falsa -------------------------------------------------------------------------------
function falsePositionScene() {
  const its = [];
  let A = 1, B = 2;
  for (let k = 1; k <= 3; k++) {
    const fa = f(A), fb = f(B), xr = B - fb * (B - A) / (fb - fa), fr = f(xr), left = fa * fr < 0;
    its.push({k, a: A, b: B, fa, fb, xr, fr, left});
    if (left) B = xr; else A = xr;
  }
  const frames = [{
    title: 'Unir los extremos con una recta',
    text: 'Se parte del mismo intervalo [1, 2]. En lugar del punto medio se usa el corte con el eje de la recta que une (a, f(a)) y (b, f(b)).',
    tex: String.raw`x_r=b-\frac{f(b)\,(b-a)}{f(b)-f(a)}`,
    step: null, row: null,
    draw(p, {current}) {
      if (!current) return;
      p.band(1, 2);
      p.point(1, f(1), 'anim-point anim-point-neg');
      p.point(2, f(2), 'anim-point anim-point-pos');
      p.label(1, f(1), 'a = 1', {dy: 24});
      p.label(2, f(2), 'b = 2', {dx: -10, dy: 5, anchor: 'end'});
    },
  }];
  its.forEach(it => frames.push({
    title: `Corte ${it.k}: x${sub(it.k)} = ${n6(it.xr)}`,
    text: `La recta entre (${ns(it.a)}, ${ns(it.fa)}) y (${ns(it.b)}, ${ns(it.fb)}) corta el eje en ${n6(it.xr)}. Como f(x${sub(it.k)}) = ${n6(it.fr)} tiene el signo de f(${it.left ? 'b' : 'a'}), ${it.left ? 'b' : 'a'} pasa a ser ${n6(it.xr)}.`,
    tex: String.raw`x_{${it.k}}=${ts(it.b)}-\frac{${ts(it.fb)}\,(${ts(it.b)}-${ts(it.a)})}{${ts(it.fb)}-${paren(ts(it.fa))}}=${t6(it.xr)}`,
    step: it.k - 1, row: it.k - 1,
    draw(p, {current}) {
      p.line(it.a, it.fa, it.b, it.fb, current ? 'anim-line anim-chord' : 'anim-line anim-chord anim-thin');
      p.point(it.xr, 0, 'anim-point anim-point-axis', current ? 5.5 : 3.5);
      if (!current) return;
      p.band(it.a, it.b);
      p.point(it.a, it.fa, 'anim-point anim-point-muted', 4);
      p.point(it.b, it.fb, 'anim-point anim-point-muted', 4);
      p.line(it.xr, 0, it.xr, it.fr, 'anim-line anim-dashed');
      p.point(it.xr, it.fr, 'anim-point anim-point-accent');
      p.tag(it.xr, `x${sub(it.k)}`, {above: true});
    },
  }));
  const last = its[its.length - 1], na = last.left ? last.a : last.xr;
  frames.push({
    title: 'El extremo b no se mueve',
    text: `Las aproximaciones llegan solo por la izquierda y b = 2 queda fijo. La anchura del intervalo [${n6(na)}, 2] = ${n6(2 - na)} no tiende a cero, por eso no sirve como cota del error.`,
    tex: String.raw`b-a=2-${t6(na)}=${t6(2 - na)}\not\to0`,
    step: null, row: null,
    draw(p, {current}) {
      if (!current) return;
      p.band(na, 2, 'anim-band-keep');
      p.ring(2, f(2));
      p.label(2, f(2), 'b fijo', {dx: -14, dy: -12, anchor: 'end'});
      p.point(ROOT, 0, 'anim-point anim-point-root');
    },
  });
  return {title: 'Regla falsa en [1, 2]', view: {x: [0.85, 2.15], y: [-2.8, 4.8]}, base: cubicBase, legend: CUBIC_LEGEND, frames};
}

// ---- Newton-Raphson ----------------------------------------------------------------------------
export function newtonIterations(x0, n) {
  const out = [];
  let x = x0;
  for (let k = 0; k < n; k++) {
    const fx = f(x), dfx = df(x), next = x - fx / dfx;
    out.push({k, x, fx, dfx, next});
    x = next;
  }
  return out;
}
export function newtonTangentFrame(it, {step = null, row = null, view} = {}) {
  const xs = `x${sub(it.k)}`;
  return {
    title: `Tangente en ${xs} = ${ns(it.x)}`,
    text: `f(${xs}) = ${n6(it.fx)} y f′(${xs}) = ${n6(it.dfx)}: la recta tangente en (${xs}, f(${xs})) tiene pendiente ${n6(it.dfx)}.`,
    tex: String.raw`f(${ts(it.x)})=${t6(it.fx)},\qquad f'(${ts(it.x)})=${t6(it.dfx)}`,
    step, row, view,
    draw(p, {current}) {
      p.fullLine(it.x, it.fx, it.dfx, current ? 'anim-line anim-tangent' : 'anim-line anim-tangent anim-thin');
      p.point(it.x, it.fx, current ? 'anim-point anim-point-accent' : 'anim-point anim-point-muted', current ? 5.5 : 3.5);
      if (current) p.tag(it.x, xs);
    },
  };
}
export function newtonCutFrame(it, {step = null, row = null, view, note = ''} = {}) {
  const xs = `x${sub(it.k)}`, xn = `x${sub(it.k + 1)}`;
  return {
    title: `Corte con el eje: ${xn} = ${n6(it.next)}`,
    text: `${xn} = ${xs} − f(${xs})/f′(${xs}) = ${n6(it.next)}.${note ? ` ${note}` : ''}`,
    tex: String.raw`x_{${it.k + 1}}=${ts(it.x)}-\frac{${t6(it.fx)}}{${t6(it.dfx)}}=${t6(it.next)}`,
    step, row, view,
    draw(p, {current}) {
      p.point(it.next, 0, 'anim-point anim-point-axis', current ? 5.5 : 3.5);
      if (!current) return;
      p.fullLine(it.x, it.fx, it.dfx, 'anim-line anim-tangent');
      p.line(it.next, 0, it.next, f(it.next), 'anim-line anim-dashed');
      p.tag(it.next, xn, {above: it.fx > 0});
    },
  };
}
function newtonScene() {
  const its = newtonIterations(1.5, 3);
  const wide = {x: [1.0, 2.1], y: [-2.5, 5]};
  const zoom = {x: [1.49, 1.55], y: [-0.16, 0.2]};
  const close = {x: [1.5206, 1.5222], y: [-0.0045, 0.0055]};
  const errors = [its[0].x, its[0].next, its[1].next, its[2].next].map(x => sci(Math.abs(x - ROOT), 1));
  return {
    title: 'Newton-Raphson desde x₀ = 1.5', view: wide, base: cubicBase, legend: CUBIC_LEGEND,
    frames: [
      newtonTangentFrame(its[0], {step: 0, row: 0, view: wide}),
      newtonCutFrame(its[0], {step: 1, row: 0, view: wide}),
      {...newtonTangentFrame(its[1], {step: 2, row: 1, view: zoom}), title: 'Vista ampliada: tangente en x₁'},
      newtonCutFrame(its[1], {step: 2, row: 1, view: zoom}),
      newtonCutFrame(its[2], {step: 2, row: 2, view: close,
        note: `Los errores |xₙ − r| son ${errors.join(' → ')}: los decimales correctos se duplican en cada paso (convergencia cuadrática).`}),
    ],
  };
}

// ---- Secante -----------------------------------------------------------------------------------
function secantScene() {
  const its = [];
  let prev = 1, cur = 2;
  for (let k = 1; k <= 4; k++) {
    const fp = f(prev), fc = f(cur), next = cur - fc * (cur - prev) / (fc - fp);
    its.push({k, prev, cur, fp, fc, next, fn: f(next)});
    prev = cur; cur = next;
  }
  const steps = [0, 1, 1, 2];
  const frames = its.map(it => {
    const over = it.next > ROOT && it.cur < ROOT;
    return {
      title: `Secante ${it.k}: x${sub(it.k + 1)} = ${n6(it.next)}`,
      text: `Con (${ns(it.prev)}, ${ns(it.fp)}) y (${ns(it.cur)}, ${ns(it.fc)}) la recta secante corta el eje en ${n6(it.next)}; f = ${n6(it.fn)}.${over ? ' Esta vez se pasa de la raíz: la secante no conserva un intervalo.' : ''}`,
      tex: String.raw`x_{${it.k + 1}}=${ts(it.cur)}-\frac{${ts(it.fc)}\,(${ts(it.cur)}-${ts(it.prev)})}{${ts(it.fc)}-${paren(ts(it.fp))}}=${t6(it.next)}`,
      step: steps[it.k - 1], row: it.k - 1,
      draw(p, {current}) {
        p.fullLine(it.cur, it.fc, slope(it.prev, it.fp, it.cur, it.fc), current ? 'anim-line anim-chord' : 'anim-line anim-chord anim-thin');
        p.point(it.next, 0, 'anim-point anim-point-axis', current ? 5.5 : 3.5);
        if (!current) return;
        p.point(it.prev, it.fp, 'anim-point anim-point-muted', 4.5);
        p.point(it.cur, it.fc, 'anim-point anim-point-muted', 4.5);
        p.line(it.next, 0, it.next, it.fn, 'anim-line anim-dashed');
        p.point(it.next, it.fn, 'anim-point anim-point-accent');
        p.tag(it.next, `x${sub(it.k + 1)}`, {above: it.fn < 0});
      },
    };
  });
  const last = its[its.length - 1];
  frames.push({
    title: 'Orden de convergencia ≈ 1.618',
    text: `x₅ = ${n6(last.next)} está a ${sci(Math.abs(last.next - ROOT), 1)} de la raíz. Más rápido que bisección, algo más lento que Newton, y sin calcular f′.`,
    tex: String.raw`|x_5-r|\approx${texSci(Math.abs(last.next - ROOT), 1)}`,
    step: null, row: null,
    draw(p, {current}) {
      if (!current) return;
      p.point(ROOT, 0, 'anim-point anim-point-root');
      p.ring(ROOT, 0);
    },
  });
  return {title: 'Secante desde x₀ = 1, x₁ = 2', view: {x: [0.9, 2.1], y: [-2.6, 4.6]}, base: cubicBase, legend: CUBIC_LEGEND, frames};
}

// ---- Punto fijo (diagrama de telaraña) ---------------------------------------------------------
function fixedPointScene() {
  const g = x => Math.cbrt(x + 2), dg = x => (x + 2) ** (-2 / 3) / 3;
  const its = [];
  let x = 1.5;
  for (let k = 0; k < 4; k++) {const gx = g(x); its.push({k, x, gx, step: Math.abs(gx - x)}); x = gx;}
  const CLOSE = {x: [1.5196, 1.5226], y: [1.5196, 1.5226]};
  const ratios = its.slice(1).map((it, i) => ns(its[i].step / it.step, 2));
  const frames = [{
    title: 'Elegir una g que contraiga',
    text: `El punto fijo r = g(r) es la intersección de y = g(x) con y = x. Cerca de r, |g′(r)| ≈ ${ns(dg(ROOT), 3)} < 1: la curva es mucho más plana que la diagonal y la iteración converge.`,
    tex: String.raw`g(x)=\sqrt[3]{x+2},\qquad |g'(r)|\approx${ts(dg(ROOT), 3)}<1`,
    step: 0, row: null,
    draw(p, {current}) {
      if (!current) return;
      p.fullLine(ROOT, ROOT, dg(ROOT), 'anim-line anim-tangent anim-dashed');
      p.point(ROOT, ROOT, 'anim-point anim-point-root');
      p.ring(ROOT, ROOT);
      p.label(ROOT, ROOT, 'r = g(r)', {dx: 14, dy: 20, anchor: 'start'});
    },
  }];
  its.forEach(it => frames.push({
    title: `Iteración ${it.k + 1}: x${sub(it.k + 1)} = g(x${sub(it.k)})${it.k === 2 ? ' (vista ampliada)' : ''}`,
    text: `Sube de (x${sub(it.k)}, x${sub(it.k)}) hasta la curva: g(${n6(it.x)}) = ${n6(it.gx)}. Luego se lleva a la diagonal, que convierte ese valor en el nuevo x. Paso |g(x) − x| = ${n6(it.step)}.`,
    tex: String.raw`x_{${it.k + 1}}=g(x_{${it.k}})=\sqrt[3]{${ts(it.x)}+2}=${t6(it.gx)}`,
    step: 1, row: it.k, view: it.k >= 2 ? CLOSE : undefined,
    draw(p, {current}) {
      const cls = current ? 'anim-line anim-cobweb' : 'anim-line anim-cobweb anim-thin';
      p.line(it.x, it.x, it.x, it.gx, cls);
      p.line(it.x, it.gx, it.gx, it.gx, cls);
      if (!current) return;
      p.point(it.x, it.x, 'anim-point anim-point-muted', 4);
      p.point(it.x, it.gx, 'anim-point anim-point-accent');
      p.point(it.gx, it.gx, 'anim-point anim-point-axis', 4.5);
      p.tag(it.x, `x${sub(it.k)}`, {above: true});
    },
  }));
  frames.push({
    title: 'Observar el ritmo',
    text: `Cada paso es unas ${ratios.join(', ')} veces menor que el anterior (≈ 1/|g′(r)|): convergencia lineal. Con g(x) = x³ − 2, |g′| ≈ 6.9 > 1 y la telaraña se abriría hacia fuera.`,
    tex: String.raw`\frac{|x_{n+1}-x_n|}{|x_{n+2}-x_{n+1}|}\approx\frac{1}{|g'(r)|}\approx${ts(1 / dg(ROOT), 1)}`,
    step: 2, row: 3, view: CLOSE,
    draw(p, {current}) {if (current) {p.point(ROOT, ROOT, 'anim-point anim-point-root'); p.ring(ROOT, ROOT);}},
  });
  return {
    title: 'Punto fijo con g(x) = (x + 2)^(1/3)', view: {x: [1.495, 1.548], y: [1.495, 1.548]},
    base: p => {p.axes({yLabel: 'y', zeroLine: false}); p.curve(t => t, {cls: 'anim-diagonal'}); p.curve(g);},
    legend: [['y = g(x)', 'anim-curve'], ['y = x', 'anim-diagonal']], frames,
  };
}

// ---- Raíces múltiples -------------------------------------------------------------------------
function multipleRootsScene() {
  const p3 = x => (x - 1) ** 2 * (x + 2), d1 = x => 3 * x * x - 3, d2 = x => 6 * x;
  const mod = [1.8], ord = [1.8];
  for (let k = 0; k < 4; k++) {
    const m = mod[k]; mod.push(m - p3(m) * d1(m) / (d1(m) ** 2 - p3(m) * d2(m)));
    const o = ord[k]; ord.push(o - p3(o) / d1(o));
  }
  const frames = [{
    title: 'Reconocer la multiplicidad',
    text: 'En x = 1 la curva toca el eje sin cruzarlo: p(1) = 0 y p′(1) = 0, raíz doble. Newton ordinario pierde allí la convergencia cuadrática.',
    tex: String.raw`p(x)=(x-1)^2(x+2),\qquad p(1)=p'(1)=0`,
    step: 0, row: null,
    draw(p, {current}) {
      if (!current) return;
      p.line(0.75, 0, 1.25, 0, 'anim-line anim-tangent anim-dashed');
      p.point(1, 0, 'anim-point anim-point-root');
      p.ring(1, 0);
      p.label(1, 0, 'p(1) = 0 y p′(1) = 0', {dy: -20});
      p.point(1.8, p3(1.8), 'anim-point anim-point-muted');
      p.label(1.8, p3(1.8), 'x₀ = 1.8', {dx: -10, dy: 4, anchor: 'end'});
    },
  }];
  for (let k = 1; k <= 3; k++) {
    const m0 = mod[k - 1], m1 = mod[k], o0 = ord[k - 1], o1 = ord[k];
    frames.push({
      title: `Paso ${k}: modificado frente a ordinario`,
      text: `Newton modificado: x${sub(k)} = ${n6(m1)}. Newton ordinario desde el mismo inicio: ${n6(o1)}, todavía a ${n6(o1 - 1)} de la raíz.`,
      tex: String.raw`x_{${k}}=${ts(m0)}-\frac{(${texSci(p3(m0))})(${texSci(d1(m0))})}{(${texSci(d1(m0))})^2-(${texSci(p3(m0))})(${texSci(d2(m0))})}=${t6(m1)}`,
      step: 1, row: k - 1,
      draw(p, {current}) {
        const thin = current ? '' : ' anim-thin';
        p.line(o0, p3(o0), o1, 0, `anim-line anim-ordinary${thin}`);
        p.point(o1, 0, 'anim-point anim-point-ordinary', current ? 5 : 3.5);
        const x0 = p.X(m0), x1 = p.X(m1), y = p.Y(0), lift = Math.min(70, Math.abs(x1 - x0) * 0.45 + 18);
        p.raw('path', {d: `M${x0},${y - 6}Q${(x0 + x1) / 2},${y - 6 - lift} ${x1},${y - 6}`, pathLength: 1}, `anim-jump anim-draw${thin}`);
        p.point(m1, 0, 'anim-point anim-point-accent', current ? 5.5 : 3.5);
        if (!current) return;
        p.point(o0, p3(o0), 'anim-point anim-point-ordinary', 4.5);
        p.tag(o1, `ord. ${ns(o1, 3)}`);
      },
    });
  }
  const errs = ord.slice(0, 5).map(x => ns(Math.abs(x - 1), 3));
  frames.push({
    title: 'Contrastar con Newton ordinario',
    text: `Errores de Newton ordinario: ${errs.join(' → ')}. Cada paso solo reduce el error a la mitad (factor (m − 1)/m = 1/2). El modificado llega a 1.000000 en tres pasos, a cambio de calcular también p″.`,
    tex: String.raw`\frac{|x_{n+1}-1|}{|x_n-1|}\to\frac{m-1}{m}=\frac12`,
    step: 2, row: null,
    draw(p, {current}) {
      if (!current) return;
      p.line(ord[3], p3(ord[3]), ord[4], 0, 'anim-line anim-ordinary');
      p.point(ord[4], 0, 'anim-point anim-point-ordinary');
      p.ring(1, 0);
    },
  });
  return {
    title: 'Raíz doble: Newton modificado y ordinario', view: {x: [0.85, 1.9], y: [-0.4, 2.7]}, legendAt: 'top-left',
    base: p => {p.axes({yLabel: 'p(x)'}); p.curve(p3);},
    legend: [['p(x) = (x − 1)²(x + 2)', 'anim-curve'], ['Modificado', 'anim-jump'], ['Ordinario', 'anim-ordinary']],
    frames,
  };
}

// ---- Caso del informe (tema «Raíces»): bisección y primera tangente de Newton -------------------
function rootsCaseScene() {
  const its = bisectionIterations(f, 1, 2, 3), nt = newtonIterations(1.5, 1)[0];
  return {
    title: 'Una ecuación, dos recorridos', view: {x: [0.85, 2.15], y: [-2.8, 4.8]}, base: cubicBase, legend: CUBIC_LEGEND,
    frames: [
      signFrame(1, 2),
      ...its.map(it => bisectionFrame(it)),
      {...newtonTangentFrame(nt), title: 'Newton: tangente en x₀ = 1.5'},
      {...newtonCutFrame(nt, {note: 'Con un solo paso ya está más cerca de la raíz que las tres bisecciones.'}), title: `Newton: x₁ = ${n6(nt.next)}`},
    ],
  };
}

export const rootScenes = {
  bisection: bisectionScene,
  'false-position': falsePositionScene,
  newton: newtonScene,
  secant: secantScene,
  'fixed-point': fixedPointScene,
  'multiple-roots': multipleRootsScene,
  'roots-case': rootsCaseScene,
};
