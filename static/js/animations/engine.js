// Motor de las animaciones de teoría: un botón «Iniciar animación» abre un escenario con dos
// modos («Paso a paso» y «Automático», con velocidad ajustable). Cada escena es una lista de
// fotogramas; un fotograma dibuja su construcción y explica el cálculo que la produce.
import {Plot} from './plot.js';
import {setMath} from '../nonlinear/common.js';

export const SPEEDS = {
  slow: {label: 'Lento', ms: 3800},
  normal: {label: 'Normal', ms: 2400},
  fast: {label: 'Rápido', ms: 1300},
};
const SPEED_KEY = 'numlearn:animation-speed';
const storedSpeed = () => {try {const value = localStorage.getItem(SPEED_KEY); return SPEEDS[value] ? value : 'normal';} catch {return 'normal';}};

function html(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (value == null || value === false) continue;
    if (key === 'text') node.textContent = value;
    else if (key === 'html') node.innerHTML = value;
    else node.setAttribute(key, value === true ? '' : value);
  }
  node.append(...children);
  return node;
}
const ICON_PLAY = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4.5 2.8v10.4L13 8z" fill="currentColor"/></svg>';
const ICON_PAUSE = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4 2.8h2.8v10.4H4zM9.2 2.8H12v10.4H9.2z" fill="currentColor"/></svg>';
const ICON_REPLAY = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 3a5 5 0 1 1-4.9 6h1.6A3.5 3.5 0 1 0 8 4.5V7L4.5 3.8 8 .5z" fill="currentColor"/></svg>';

export class TheoryAnimation {
  constructor(root, factory) {
    this.root = root;
    this.factory = factory;
    this.key = root.dataset.scene;
    this.index = 0;
    this.mode = 'step';
    this.playing = false;
    this.speed = storedSpeed();
    this.timer = null;
    this.launch = root.querySelector('[data-anim-launch]');
    this.startButton = root.querySelector('[data-anim-start]');
    this.stage = root.querySelector('[data-anim-stage]');
    this.context = root.closest('.worked-example') || root.closest('section') || root.parentElement;
    this.launch.hidden = false;
    this.startButton.addEventListener('click', () => this.open());
    document.addEventListener('visibilitychange', () => {if (document.hidden) this.pause();});
  }

  build() {
    const id = `anim-${this.key}-${Math.random().toString(36).slice(2, 7)}`;
    this.titleNode = html('strong', {id: `${id}-title`, class: 'anim-scene-title'});
    this.modeButtons = Object.entries({step: 'Paso a paso', auto: 'Automático'}).map(([mode, label]) =>
      html('button', {type: 'button', class: 'anim-mode', 'data-mode': mode, 'aria-pressed': String(mode === this.mode), 'data-testid': `anim-mode-${mode}`, text: label}));
    this.closeButton = html('button', {type: 'button', class: 'anim-close', 'aria-label': 'Cerrar animación', title: 'Cerrar animación', 'data-testid': 'anim-close', html: '&times;'});
    const head = html('div', {class: 'anim-head'}, [
      html('div', {class: 'anim-heading'}, [html('span', {class: 'eyebrow', text: 'ANIMACIÓN DEL EJEMPLO'}), this.titleNode]),
      html('div', {class: 'anim-modes', role: 'group', 'aria-label': 'Modo de reproducción'}, this.modeButtons),
      this.closeButton,
    ]);
    this.figure = html('figure', {class: 'anim-figure'});
    this.counter = html('span', {class: 'anim-counter', 'data-testid': 'anim-counter'});
    this.captionTitle = html('h4', {class: 'anim-caption-title', 'data-testid': 'anim-caption-title'});
    this.captionText = html('p', {class: 'anim-caption-text'});
    this.captionMath = html('div', {class: 'anim-caption-math formula'});
    this.narration = html('div', {class: 'anim-narration', 'aria-live': 'polite'}, [this.counter, this.captionTitle, this.captionText, this.captionMath]);
    this.timeline = html('ol', {class: 'anim-timeline', 'aria-label': 'Pasos de la animación'});
    this.prevButton = html('button', {type: 'button', class: 'btn btn-light', 'data-testid': 'anim-prev', html: '← Anterior'});
    this.nextButton = html('button', {type: 'button', class: 'btn btn-primary', 'data-testid': 'anim-next', html: 'Siguiente paso →'});
    this.playButton = html('button', {type: 'button', class: 'btn btn-primary anim-play', 'data-testid': 'anim-play'});
    this.speedButtons = Object.entries(SPEEDS).map(([key, {label}]) =>
      html('button', {type: 'button', class: 'anim-speed', 'data-speed': key, 'aria-pressed': String(key === this.speed), 'data-testid': `anim-speed-${key}`, text: label}));
    this.restartButton = html('button', {type: 'button', class: 'btn btn-light anim-restart', 'data-testid': 'anim-restart', html: `${ICON_REPLAY} Reiniciar`});
    this.stepControls = html('div', {class: 'anim-step-controls'}, [this.prevButton, this.nextButton]);
    this.autoControls = html('div', {class: 'anim-auto-controls', hidden: true}, [
      this.playButton,
      html('div', {class: 'anim-speeds', role: 'group', 'aria-label': 'Velocidad'}, [html('span', {class: 'anim-speed-label', text: 'Velocidad'}), ...this.speedButtons]),
    ]);
    const controls = html('div', {class: 'anim-controls'}, [this.stepControls, this.autoControls, this.restartButton]);
    const body = html('div', {class: 'anim-body'}, [this.figure, this.narration]);
    this.stage.replaceChildren(head, body, this.timeline, controls);
    this.stage.setAttribute('role', 'region');
    this.stage.setAttribute('aria-labelledby', this.titleNode.id);
    this.stage.tabIndex = -1;

    this.modeButtons.forEach(button => button.addEventListener('click', () => this.setMode(button.dataset.mode)));
    this.closeButton.addEventListener('click', () => this.close());
    this.prevButton.addEventListener('click', () => this.go(this.index - 1));
    this.nextButton.addEventListener('click', () => this.go(this.index + 1));
    this.playButton.addEventListener('click', () => this.playing ? this.pause() : this.play());
    this.restartButton.addEventListener('click', () => this.restart());
    this.speedButtons.forEach(button => button.addEventListener('click', () => this.setSpeed(button.dataset.speed)));
    this.stage.addEventListener('keydown', event => this.onKey(event));
    this.built = true;
  }

  load() {
    this.scene = this.factory(this.root);
    this.titleNode.textContent = this.scene.title;
    this.figure.replaceChildren();
    if (this.scene.kind === 'html') {
      this.board = html('div', {class: `anim-board anim-board-${this.key}`});
      this.figure.append(this.board);
    } else {
      this.svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      this.svg.classList.add('anim-svg');
      this.figure.append(this.svg);
    }
    if (this.scene.figcaption) this.figure.append(html('figcaption', {text: this.scene.figcaption}));
    this.timeline.replaceChildren(...this.scene.frames.map((frame, index) => {
      const button = html('button', {type: 'button', 'aria-label': `Paso ${index + 1}: ${frame.title}`, title: frame.title, 'data-testid': `anim-dot-${index}`}, [html('span', {class: 'anim-dot-fill'})]);
      button.addEventListener('click', () => {this.pause(); this.go(index);});
      return html('li', {}, [button]);
    }));
  }

  open() {
    if (!this.built) this.build();
    this.load();
    this.launch.hidden = true;
    this.stage.hidden = false;
    this.root.classList.add('is-open');
    this.startButton.setAttribute('aria-expanded', 'true');
    this.go(0);
    this.stage.focus({preventScroll: true});
    this.stage.scrollIntoView({behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'nearest'});
    if (this.mode === 'auto') this.play();
  }

  close() {
    this.pause();
    this.stage.hidden = true;
    this.launch.hidden = false;
    this.root.classList.remove('is-open');
    this.startButton.setAttribute('aria-expanded', 'false');
    this.highlight(null);
    this.startButton.focus();
  }

  restart() {
    this.load();
    this.go(0);
    if (this.mode === 'auto') this.play();
  }

  setMode(mode) {
    this.mode = mode;
    this.modeButtons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.mode === mode)));
    this.stepControls.hidden = mode !== 'step';
    this.autoControls.hidden = mode !== 'auto';
    this.root.dataset.mode = mode;
    if (mode === 'auto') this.play(); else this.pause();
  }

  setSpeed(speed) {
    this.speed = speed;
    try {localStorage.setItem(SPEED_KEY, speed);} catch {}
    this.speedButtons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.speed === speed)));
    if (this.playing) this.schedule();
  }

  play() {
    if (!this.scene) return;
    if (this.index >= this.scene.frames.length - 1) this.go(0);
    this.playing = true;
    this.root.classList.add('is-playing');
    this.syncButtons();
    this.schedule();
  }

  pause() {
    this.playing = false;
    clearTimeout(this.timer);
    this.root.classList.remove('is-playing');
    if (this.built) this.syncButtons();
  }

  schedule() {
    clearTimeout(this.timer);
    if (!this.playing) return;
    const last = this.scene.frames.length - 1;
    this.timeline.style.setProperty('--anim-duration', `${SPEEDS[this.speed].ms}ms`);
    this.restartTimingDot();
    if (this.index >= last) {this.playing = false; this.root.classList.remove('is-playing'); this.syncButtons(); return;}
    this.timer = setTimeout(() => {
      if (!this.root.isConnected || this.root.closest('[hidden]')) {this.pause(); return;}
      this.go(this.index + 1);
    }, SPEEDS[this.speed].ms);
  }

  restartTimingDot() {
    this.timeline.querySelectorAll('button').forEach((button, index) => {
      button.classList.remove('is-timing');
      if (index === this.index && this.playing && index < this.scene.frames.length - 1) {void button.offsetWidth; button.classList.add('is-timing');}
    });
  }

  go(index) {
    const frames = this.scene.frames;
    this.index = Math.max(0, Math.min(frames.length - 1, index));
    const frame = frames[this.index];
    this.render();
    this.counter.textContent = `Paso ${this.index + 1} de ${frames.length}`;
    this.captionTitle.textContent = frame.title;
    this.captionText.textContent = frame.text || '';
    this.captionMath.hidden = !frame.tex;
    if (frame.tex) setMath(this.captionMath, frame.tex, frame.plain || '');
    this.timeline.querySelectorAll('button').forEach((button, i) => {
      button.classList.toggle('is-done', i < this.index);
      button.classList.toggle('is-current', i === this.index);
      if (i === this.index) button.setAttribute('aria-current', 'step'); else button.removeAttribute('aria-current');
    });
    this.highlight(frame);
    this.syncButtons();
    if (this.playing) this.schedule();
  }

  render() {
    const frames = this.scene.frames, frame = frames[this.index];
    const state = {index: this.index, scene: this.scene};
    if (this.scene.kind === 'html') {
      this.board.replaceChildren();
      frame.render(this.board, state);
      return;
    }
    const plot = new Plot(this.svg, frame.view || this.scene.view, {label: `${this.scene.title}. ${frame.title}`, pad: this.scene.pad});
    plot.mode = 'base';
    this.scene.base?.(plot, state);
    frames.slice(0, this.index + 1).forEach((item, k) => {
      plot.mode = k === this.index ? 'new' : 'past';
      item.draw?.(plot, {...state, current: k === this.index, k});
    });
    plot.mode = 'base';
    this.scene.legend && plot.legend(this.scene.legend, this.scene.legendAt);
  }

  // Resalta el paso de la lista y la fila de la tabla del ejercicio que explica el fotograma.
  highlight(frame) {
    const context = this.context;
    if (!context) return;
    const steps = [...context.querySelectorAll('.worked-list > li')];
    const rows = [...context.querySelectorAll('.worked-grid tbody tr')];
    const rowIndex = frame?.row === -1 ? rows.length - 1 : frame?.row;
    steps.forEach((item, i) => item.classList.toggle('anim-highlight', frame != null && i === frame.step));
    rows.forEach((row, i) => row.classList.toggle('anim-highlight', frame != null && i === rowIndex));
  }

  syncButtons() {
    const last = this.scene ? this.scene.frames.length - 1 : 0;
    this.prevButton.disabled = this.index === 0;
    this.nextButton.disabled = this.index >= last;
    this.nextButton.innerHTML = this.index >= last ? 'Fin del ejemplo' : 'Siguiente paso →';
    const ended = !this.playing && this.index >= last;
    this.playButton.innerHTML = this.playing ? `${ICON_PAUSE} Pausar` : ended ? `${ICON_REPLAY} Repetir` : `${ICON_PLAY} Reproducir`;
    this.playButton.setAttribute('aria-pressed', String(this.playing));
  }

  onKey(event) {
    if (event.target.closest('input,select,textarea')) return;
    const keys = {ArrowRight: () => this.go(this.index + 1), ArrowLeft: () => this.go(this.index - 1),
      Home: () => this.go(0), End: () => this.go(this.scene.frames.length - 1), Escape: () => this.close()};
    if (event.key === ' ' && this.mode === 'auto' && !event.target.closest('button')) {event.preventDefault(); this.playing ? this.pause() : this.play(); return;}
    const action = keys[event.key];
    if (!action || event.target.closest('.anim-timeline')) return;
    event.preventDefault();
    if (event.key !== 'Escape') this.pause();
    action();
  }
}
