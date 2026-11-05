// Dibujo SVG mínimo para las animaciones de teoría: ejes, curvas, rectas, puntos y etiquetas.
// Cada elemento recibe la clase del «modo» actual: 'new' (paso que se está explicando, entra
// animado), 'past' (pasos anteriores, atenuados) o 'base' (ejes y curva, siempre visibles).
const NS = 'http://www.w3.org/2000/svg';
export const WIDTH = 640, HEIGHT = 360;
let uid = 0;

export function svgEl(tag, attrs = {}, parent = null) {
  const node = document.createElementNS(NS, tag);
  for (const [key, value] of Object.entries(attrs)) if (value != null && value !== false) node.setAttribute(key, value);
  parent?.append(node);
  return node;
}

function niceStep(span, count = 5) {
  const raw = span / count, power = 10 ** Math.floor(Math.log10(raw)), unit = raw / power;
  return (unit < 1.5 ? 1 : unit < 3.5 ? 2 : unit < 7.5 ? 5 : 10) * power;
}
export function ticks(min, max, count = 5) {
  const step = niceStep(max - min, count), out = [];
  for (let value = Math.ceil(min / step) * step; value <= max + step * 1e-9; value += step) out.push(Number(value.toPrecision(12)));
  return out;
}
const tickText = value => {
  const text = Math.abs(value) < 1e-12 ? '0' : String(Number(value.toPrecision(6)));
  return text.replace('-', '−');
};

export class Plot {
  constructor(svg, view, {pad = {}, label = ''} = {}) {
    this.svg = svg;
    svg.replaceChildren();
    svg.setAttribute('viewBox', `0 0 ${WIDTH} ${HEIGHT}`);
    svg.setAttribute('role', 'img');
    if (label) svg.setAttribute('aria-label', label);
    this.pad = {l: 54, r: 20, t: 20, b: 38, ...pad};
    [this.x0, this.x1] = view.x;
    [this.y0, this.y1] = view.y;
    this.mode = 'base';
    const id = `anim-clip-${++uid}`;
    const defs = svgEl('defs', {}, svg);
    const clip = svgEl('clipPath', {id}, defs);
    svgEl('rect', {x: this.pad.l, y: this.pad.t, width: WIDTH - this.pad.l - this.pad.r, height: HEIGHT - this.pad.t - this.pad.b}, clip);
    this.grid = svgEl('g', {class: 'anim-grid'}, svg);
    this.area = svgEl('g', {'clip-path': `url(#${id})`}, svg);
    this.overlay = svgEl('g', {class: 'anim-overlay'}, svg);
  }
  get left() {return this.pad.l;}
  get right() {return WIDTH - this.pad.r;}
  get top() {return this.pad.t;}
  get bottom() {return HEIGHT - this.pad.b;}
  X(x) {return this.pad.l + (x - this.x0) / (this.x1 - this.x0) * (WIDTH - this.pad.l - this.pad.r);}
  Y(y) {return HEIGHT - this.pad.b - (y - this.y0) / (this.y1 - this.y0) * (HEIGHT - this.pad.t - this.pad.b);}
  cls(name = '') {
    const state = this.mode === 'new' ? 'is-new' : this.mode === 'past' ? 'is-past' : '';
    return [name, state].filter(Boolean).join(' ');
  }
  axes({xLabel = 'x', yLabel = 'y', xTicks = 6, yTicks = 5, zeroLine = true} = {}) {
    const g = this.grid;
    for (const value of ticks(this.x0, this.x1, xTicks)) {
      const x = this.X(value);
      svgEl('line', {x1: x, x2: x, y1: this.top, y2: this.bottom, class: 'anim-gridline'}, g);
      svgEl('text', {x, y: this.bottom + 20, class: 'anim-tick', 'text-anchor': 'middle'}, g).textContent = tickText(value);
    }
    for (const value of ticks(this.y0, this.y1, yTicks)) {
      const y = this.Y(value);
      svgEl('line', {x1: this.left, x2: this.right, y1: y, y2: y, class: 'anim-gridline'}, g);
      svgEl('text', {x: this.left - 8, y: y + 4, class: 'anim-tick', 'text-anchor': 'end'}, g).textContent = tickText(value);
    }
    svgEl('rect', {x: this.left, y: this.top, width: this.right - this.left, height: this.bottom - this.top, class: 'anim-frame'}, g);
    if (zeroLine && this.y0 < 0 && this.y1 > 0) svgEl('line', {x1: this.left, x2: this.right, y1: this.Y(0), y2: this.Y(0), class: 'anim-axis'}, g);
    if (zeroLine && this.x0 < 0 && this.x1 > 0) svgEl('line', {x1: this.X(0), x2: this.X(0), y1: this.top, y2: this.bottom, class: 'anim-axis'}, g);
    svgEl('text', {x: this.right - 4, y: this.bottom - 8, class: 'anim-axis-label', 'text-anchor': 'end'}, g).textContent = xLabel;
    svgEl('text', {x: this.left + 8, y: this.top + 16, class: 'anim-axis-label'}, g).textContent = yLabel;
  }
  curve(f, {cls = 'anim-curve', samples = 360, from = this.x0, to = this.x1} = {}) {
    let d = '', open = false;
    const limit = (this.y1 - this.y0) * 6;
    for (let i = 0; i <= samples; i++) {
      const x = from + (to - from) * i / samples, y = f(x);
      if (!Number.isFinite(y) || y > this.y1 + limit || y < this.y0 - limit) {open = false; continue;}
      d += `${open ? 'L' : 'M'}${this.X(x).toFixed(2)},${this.Y(y).toFixed(2)}`;
      open = true;
    }
    return this.stroke(d, cls);
  }
  // Las líneas punteadas no usan pathLength (escalaría también el patrón del trazo).
  stroke(d, cls) {
    const dashed = /anim-(dashed|diagonal)/.test(cls);
    return svgEl('path', {d, class: this.cls(dashed ? cls : `${cls} anim-draw`), pathLength: dashed ? null : 1}, this.area);
  }
  line(x1, y1, x2, y2, cls = 'anim-line') {
    return this.stroke(`M${this.X(x1)},${this.Y(y1)}L${this.X(x2)},${this.Y(y2)}`, cls);
  }
  // Recta y = y0 + m (x − x0) extendida a todo el ancho visible.
  fullLine(x0, y0, slope, cls = 'anim-line') {
    return this.line(this.x0, y0 + slope * (this.x0 - x0), this.x1, y0 + slope * (this.x1 - x0), cls);
  }
  band(a, b, cls = 'anim-band') {
    const x = this.X(Math.min(a, b)), w = Math.max(2, Math.abs(this.X(b) - this.X(a)));
    return svgEl('rect', {x, y: this.top, width: w, height: this.bottom - this.top, class: this.cls(`${cls} anim-fade`)}, this.area);
  }
  point(x, y, cls = 'anim-point', r = 5.5) {
    return svgEl('circle', {cx: this.X(x), cy: this.Y(y), r, class: this.cls(`${cls} anim-pop`)}, this.area);
  }
  ring(x, y, cls = 'anim-ring', r = 13) {
    return svgEl('circle', {cx: this.X(x), cy: this.Y(y), r, class: this.cls(`${cls} anim-pulse`)}, this.area);
  }
  label(x, y, text, {cls = 'anim-label', dx = 0, dy = -12, anchor = 'middle'} = {}) {
    const node = svgEl('text', {x: this.X(x) + dx, y: this.Y(y) + dy, 'text-anchor': anchor, class: this.cls(`${cls} anim-fade`)}, this.overlay);
    node.textContent = text;
    return node;
  }
  // Etiqueta pegada al eje horizontal (sobre y = 0 o sobre el borde inferior si 0 no es visible).
  tag(x, text, {cls = 'anim-tag', above = false} = {}) {
    const base = this.y0 < 0 && this.y1 > 0 ? this.Y(0) : this.bottom;
    const node = svgEl('text', {x: this.X(x), y: base + (above ? -10 : 17), 'text-anchor': 'middle', class: this.cls(`${cls} anim-fade`)}, this.overlay);
    node.textContent = text;
    return node;
  }
  legend(items, at = 'bottom-right') {
    const g = svgEl('g', {class: 'anim-legend'}, this.overlay);
    const total = items.reduce((sum, [text]) => sum + 34 + text.length * 6.6, 0);
    const top = at === 'top-left' ? this.top + 6 : this.bottom - 52;
    const back = svgEl('rect', {x: at === 'top-left' ? this.left + 34 : this.right - total - 14, y: top, width: total + 6, height: 21, rx: 6, class: 'anim-legend-back'}, g);
    let x = Number(back.getAttribute('x')) + 8;
    items.forEach(([text, cls]) => {
      svgEl('line', {x1: x, x2: x + 18, y1: top + 10.5, y2: top + 10.5, class: `anim-legend-swatch ${cls}`}, g);
      const label = svgEl('text', {x: x + 24, y: top + 14.5, class: 'anim-legend-text'}, g);
      label.textContent = text;
      x += 34 + text.length * 6.6;
    });
    return g;
  }
  raw(tag, attrs, cls = '') {
    return svgEl(tag, {...attrs, class: this.cls(cls)}, this.overlay);
  }
}
