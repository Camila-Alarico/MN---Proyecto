import {post, busy, setMath} from './common.js';

const root = document.getElementById('activity');
const mode = root.dataset.mode;
const start = document.getElementById('activity-start');
const work = document.getElementById('activity-work');
const error = document.getElementById('activity-error');
let generation = 0;

// Bloqueo al salir de la página: el aviso se envía al servidor, que guarda el bloqueo en la sesión.
// Así recargar, volver más tarde o usar el botón «atrás» no recupera el avance.
let active = null, away = false, blurTimer = null;
const csrfToken = () => document.querySelector('[name=csrfmiddlewaretoken]').value;
function reportLeave() {
  if (!active) return;
  fetch(root.dataset.endpoint, {method: 'POST', credentials: 'same-origin', keepalive: true,
    headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrfToken()},
    body: JSON.stringify({action: 'leave', id: active, scope: root.dataset.scope || 'modulo'})}).catch(() => {});
}
function leave() {
  if (!active || away) return;
  away = true; reportLeave();
}
async function back() {
  if (!away) return;
  away = false;
  const id = active;
  // 'leave' es idempotente: si el aviso anterior no llegó, queda registrado ahora y el servidor responde bloqueado.
  const state = await request({action: 'leave', id});
  if (state) render(state, true);
}
document.addEventListener('visibilitychange', () => document.hidden ? leave() : (document.hasFocus() ? back() : null));
window.addEventListener('blur', () => {clearTimeout(blurTimer); blurTimer = setTimeout(() => {if (!document.hasFocus()) leave();}, 400);});
window.addEventListener('focus', () => {clearTimeout(blurTimer); if (!document.hidden) back();});
window.addEventListener('pagehide', leave);
window.addEventListener('pageshow', event => {if (event.persisted) back();});

function node(tag, className, text) {
  const item = document.createElement(tag);
  if (className) item.className = className;
  if (text !== undefined) item.textContent = text;
  return item;
}
function link(text, href, className = 'btn btn-light') {
  const item = node('a', className, text); item.href = href; return item;
}
function math(spec, className = 'practice-math', inline = false) {
  const target = node(inline ? 'span' : 'div', className);
  if (spec) setMath(target, spec.tex, spec.fallback, {inline});
  return target;
}
function clearMath(target) {window.MathJax?.typesetClear?.([target]);}
function givenValues(context) {
  const list = node('dl', 'practice-given');
  context.given.forEach(item => {
    const group = node('div'); group.append(node('dt', '', item.label));
    const value = node('dd'); value.append(math(item, 'given-value', true)); group.append(value); list.append(group);
  });
  return list;
}
function similarExample() {
  const details = node('details', 'similar-example');
  details.append(node('summary', '', 'Ver un ejemplo con otros datos'));
  const content = node('div', 'similar-example-content');
  content.append(node('p', '', 'Mismo procedimiento, otra referencia:'));
  const examples = [
    [String.raw`v=50,\quad\widetilde v=49.5,\quad\tau=0.25`, 'v = 50; aproximación = 49.5; τ = 0.25'],
    [String.raw`E_a=|50-49.5|=0.5`, 'Ea = |50 − 49.5| = 0.5'],
    [String.raw`E_r=\frac{0.5}{|50|}=0.01,\qquad E_p=1\,\%`, 'Er = 0.5 / |50| = 0.01; Ep = 1 %'],
    [String.raw`0.5>0.25\quad\Longrightarrow\quad\text{no cumple}`, '0.5 > 0.25: no cumple'],
  ];
  examples.forEach(([tex, fallback]) => content.append(math({tex, fallback})));
  content.append(node('p', '', 'Una misma distancia puede representar proporciones distintas. Usa la referencia de tu propio ejercicio.'));
  details.append(content); return details;
}
async function request(payload) {
  const version = ++generation;
  error.hidden = true;
  try {
    const result = await post(root.dataset.endpoint, {...payload, scope: root.dataset.scope || 'modulo'});
    return version === generation ? result : null;
  } catch (err) {
    if (version === generation) {error.textContent = err.message; error.hidden = false;}
    return null;
  }
}
async function begin(topic, exercise) {
  const buttons = [...start.querySelectorAll('button')];
  buttons.forEach(button => {button.disabled = true;});
  const state = await request({action: 'start', topic, ...(exercise ? {exercise} : {})});
  buttons.forEach(button => {button.disabled = false;});
  if (state) render(state, true);
}
document.querySelectorAll('[data-start-topic]').forEach(button => button.addEventListener('click', () => begin(button.dataset.startTopic, button.dataset.exercise)));

const filter = document.getElementById('practice-topic') || document.getElementById('practice-skill');
const more = document.getElementById('more-exercises');
const cards = [...document.querySelectorAll('[data-exercise-topic]')];
let visibleCount = 6;
function filterExercises() {
  const matching = cards.filter(card => filter.value === 'all' || (filter.id === 'practice-skill' ? card.dataset.exerciseSkill : card.dataset.exerciseTopic) === filter.value);
  cards.forEach(card => {card.hidden = true;});
  matching.slice(0, visibleCount).forEach(card => {card.hidden = false;});
  document.getElementById('practice-count').textContent = `${Math.min(visibleCount, matching.length)} de ${matching.length} ejercicios`;
  more.hidden = visibleCount >= matching.length;
}
if (filter) {
  const filterKey = filter.id === 'practice-skill' ? 'grupo' : 'tema';
  const topic = new URLSearchParams(location.search).get(filterKey);
  if ([...filter.options].some(option => option.value === topic)) filter.value = topic;
  filter.addEventListener('change', () => {
    visibleCount = 6; filterExercises();
    const url = new URL(location.href); url.searchParams.set(filterKey, filter.value); history.replaceState({}, '', url);
  });
  more.addEventListener('click', () => {visibleCount += 6; filterExercises(); cards.filter(card => !card.hidden).at(-6)?.querySelector('button')?.focus();});
  filterExercises();
}

function graph(curve, diagonal = false, caption = '') {
  const box = node('figure', 'practice-graph');
  const ns = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(ns, 'svg');
  svg.setAttribute('viewBox', '0 0 520 235');
  svg.setAttribute('role', 'img');
  const left = curve[0].x, right = curve.at(-1).x;
  svg.setAttribute('aria-label', `Gráfica entre ${left} y ${right}. ${caption} Los valores numéricos están disponibles debajo.`);
  const ys = curve.map(p => p.y).concat(diagonal ? [left, right] : [0]);
  const margin = Math.max((Math.max(...ys)-Math.min(...ys))*.1, .1);
  const lower = Math.min(...ys)-margin, upper = Math.max(...ys)+margin;
  const x = value => 38 + (value-left)/(right-left)*454, y = value => 192-(value-lower)/(upper-lower)*172;
  function shape(tag, attrs) {
    const element = document.createElementNS(ns, tag);
    Object.entries(attrs).forEach(([key, value]) => element.setAttribute(key, value));
    svg.append(element); return element;
  }
  if (lower <= 0 && upper >= 0) shape('line', {x1: 38, x2: 492, y1: y(0), y2: y(0), stroke: '#a1aaba'});
  shape('line', {x1: 38, x2: 38, y1: 16, y2: 196, stroke: '#a1aaba'});
  for (let i = 0; i <= 4; i++) {
    const value = left+(right-left)*i/4;
    const label = shape('text', {x: x(value), y: 219, 'text-anchor': 'middle', fill: '#53617b', 'font-size': 13}); label.textContent = Number(value.toFixed(3));
  }
  if (diagonal) shape('line', {x1: x(left), x2: x(right), y1: y(left), y2: y(right), stroke: '#9c714b', 'stroke-dasharray': '6 4', 'stroke-width': 2});
  shape('polyline', {points: curve.map(p => `${x(p.x)},${y(p.y)}`).join(' '), fill: 'none', stroke: '#6653c3', 'stroke-width': 3});
  box.append(svg, node('figcaption', '', caption));
  const details = node('details', 'graph-values'); details.append(node('summary', '', 'Consultar valores de la gráfica'));
  const table = node('table', 'table');
  const header = table.createTHead().insertRow();
  for (const title of ['x', diagonal ? 'g(x)' : 'f(x)']) header.append(node('th', '', title));
  const body = table.createTBody();
  curve.filter((_, i) => i % 4 === 0).forEach(point => {const row = body.insertRow(); row.insertCell().textContent = Number(point.x.toPrecision(8)); row.insertCell().textContent = Number(point.y.toPrecision(8));});
  details.append(table); box.append(details); return box;
}

function renderLocked(state) {
  active = null; away = false;
  clearMath(work);
  start.hidden = true; work.hidden = false; work.replaceChildren();
  const box = node('section', 'activity-card activity-locked');
  box.append(node('span', 'eyebrow', 'PRÁCTICA BLOQUEADA'));
  const title = node('h2', '', 'Saliste de la página y la práctica se bloqueó'); title.tabIndex = -1; box.append(title);
  box.append(node('p', 'activity-feedback incorrect', state.message));
  box.append(node('p', 'activity-footnote', `Ejercicio: ${state.title} · ${state.exercise_title}. Bloqueos acumulados: ${state.locks}.`));
  const actions = node('div', 'activity-actions');
  const again = node('button', 'btn btn-primary', 'Repetir desde el inicio'); again.type = 'button';
  again.addEventListener('click', async () => {
    busy(again, true, 'Reiniciando…');
    const fresh = await request({action: 'restart'});
    busy(again, false);
    if (fresh) render(fresh, true);
  });
  const other = node('button', 'btn btn-light', 'Elegir otra práctica'); other.type = 'button';
  other.addEventListener('click', () => {generation++; start.hidden = false; work.hidden = true; error.hidden = true; start.querySelector('button')?.focus();});
  actions.append(again, other); box.append(actions); work.append(box); title.focus();
}

function render(state, focus = false) {
  if (state.locked) return renderLocked(state);
  active = state.done ? null : state.id; away = false;
  clearMath(work);
  start.hidden = true; work.hidden = false; work.replaceChildren();
  if (state.done) return finish(state, focus);
  const top = node('div', 'activity-top');
  const caption = `Paso ${state.step+1} de ${state.steps.length} · ${state.steps[state.step]}`;
  top.append(node('span', 'eyebrow', caption));
  const exit = node('button', 'quiet-button', 'Elegir otra práctica');
  exit.addEventListener('click', () => {active = null; generation++; start.hidden = false; work.hidden = true; error.hidden = true; start.querySelector('button')?.focus();});
  top.append(exit); work.append(top);
  const progress = node('div', 'activity-progress');
  const bar = node('span'); bar.style.width = `${100 * state.step/state.steps.length}%`; progress.append(bar); work.append(progress);
  const card = node('section', 'activity-card');
  card.append(node('p', 'exercise-caption', `${state.title} · ${state.exercise_title}`));
  // El enunciado contextualizado va primero: el estudiante entiende la situación antes de ver los datos.
  card.append(node('p', 'activity-problem', state.context_note || state.problem));
  if (state.math_context) {
    card.classList.add('errors-practice');
    card.append(givenValues(state.math_context));
  } else if (state.problem_formula) card.append(math(state.problem_formula, 'reference-formula'));
  const heading = node('h2', '', state.prompt);
  heading.tabIndex = -1; card.append(heading);
  if (state.math_context?.known) card.append(math(state.math_context.known, 'known-result', true));
  if (state.math_context?.reference_formula) card.append(math(state.math_context.reference_formula, 'reference-formula'));
  if (state.curve && (state.step === 1 || state.step === 2)) card.append(graph(state.curve, state.diagonal, state.graph_caption));
  for (const key of ['calculation_formula', 'derivative_formula', 'second_derivative_formula']) {
    if (state[key]) card.append(math(state[key], 'reference-formula'));
  }
  if (state.hint) {const hint = node('details', 'activity-hint'); hint.append(node('summary', '', 'Necesito una pista'), node('p', '', state.hint)); card.append(hint);}
  const form = node('form', 'activity-form');
  const choices = state.choices;
  if (choices) {
    const fieldset = node('fieldset', 'activity-options');
    const legend = node('legend', 'visually-hidden', 'Selecciona una respuesta'); fieldset.append(legend);
    choices.forEach(([value, text], i) => {
      const label = node('label', 'activity-choice');
      const input = node('input'); Object.assign(input, {type: 'radio', name: 'choice', value: String(value), required: true, id: `answer-${i}`});
      label.append(input, node('span', '', text)); fieldset.append(label);
    });
    form.append(fieldset);
  } else {
    const fields = node('div', 'activity-fields');
    state.fields.forEach(field => {
      const group = node('div', 'practice-field' + (field.options ? ' field-wide' : '')); group.dataset.field = field.key;
      const label = node('label', '', field.label); label.htmlFor = `answer-${field.key}`;
      const input = node(field.options ? 'select' : 'input');
      Object.assign(input, {id: label.htmlFor, name: field.key, required: true});
      if (field.options) {
        const placeholder = node('option', '', 'Elige una respuesta'); placeholder.value = ''; input.append(placeholder);
        field.options.forEach(([value, text]) => {const option = node('option', '', text); option.value = value; input.append(option);});
      } else Object.assign(input, {type: 'number', step: 'any', inputMode: 'decimal'});
      group.append(label);
      if (field.formula) group.append(math(field.formula, 'field-formula'));
      group.append(input);
      const descriptions = [];
      if (field.note || field.hint) {
        const note = node('small', 'field-note', field.note || field.hint); note.id = `note-${field.key}`;
        group.append(note); descriptions.push(note.id);
      }
      const checked = node('div', 'field-check'); checked.id = `check-${field.key}`; checked.hidden = true;
      group.append(checked); descriptions.push(checked.id); input.setAttribute('aria-describedby', descriptions.join(' '));
      input.addEventListener('input', () => {
        input.removeAttribute('aria-invalid'); group.classList.remove('field-correct', 'field-incorrect'); checked.hidden = true;
      });
      fields.append(group);
    });
    form.append(fields, node('p', 'activity-footnote', 'Usa punto decimal. Si necesitas redondear, conserva al menos seis decimales.'));
  }
  const feedback = node('div', 'activity-feedback'); feedback.setAttribute('role', 'status'); feedback.tabIndex = -1; feedback.hidden = true;
  const actions = node('div', 'activity-actions');
  const submit = node('button', 'btn btn-primary', 'Comprobar respuesta'); submit.type = 'submit'; actions.append(submit);
  form.append(feedback, actions); card.append(form); work.append(card);
  if (state.topic === 'errores' && state.step === 4 && !state.reference_zero) card.append(similarExample());
  form.addEventListener('submit', async event => {
    event.preventDefault(); if (!form.reportValidity()) return;
    const data = Object.fromEntries(new FormData(form));
    busy(submit, true, 'Comprobando…');
    const result = await request({action: 'check', id: state.id, step: state.step, ...data});
    busy(submit, false);
    if (!result) {
      // Si otra pestaña o un aviso previo bloqueó la práctica, el servidor lo sabe: se muestra el bloqueo.
      const current = await request({action: 'resume'});
      if (current?.locked) render(current, true);
      return;
    }
    feedback.hidden = false; feedback.className = `activity-feedback ${result.correct ? 'correct' : 'incorrect'}`;
    feedback.textContent = `${result.correct ? '✓ ' : result.checks?.length ? '' : 'Revisa este paso. '}${result.feedback}`;
    for (const item of result.checks || []) {
      const group = form.querySelector(`[data-field="${item.field}"]`);
      if (!group) continue;
      const checked = group.querySelector('.field-check'), input = group.querySelector('input, select');
      clearMath(checked); checked.replaceChildren(); checked.hidden = false;
      checked.append(node('p', '', `${item.correct ? '✓ ' : '↳ '}${item.message}`));
      if (!item.correct && item.formula) checked.append(math(item.formula, 'check-formula'));
      group.classList.toggle('field-correct', item.correct); group.classList.toggle('field-incorrect', !item.correct);
      input.setAttribute('aria-invalid', String(!item.correct));
    }
    const invalid = form.querySelector('[aria-invalid="true"]');
    if (invalid) invalid.focus(); else feedback.focus();
    if (result.correct) {
      form.querySelectorAll('input, select').forEach(input => {input.disabled = true;}); submit.hidden = true;
      const next = node('button', 'btn btn-primary', result.state.done ? 'Ver resultado →' : 'Continuar →'); next.type = 'button';
      next.addEventListener('click', () => render(result.state, true)); actions.append(next);
    }
  });
  if (focus) heading.focus();
}

function finish(state, focus) {
  const box = node('section', 'activity-card activity-result');
  box.append(node('span', 'eyebrow', 'RECORRIDO COMPLETADO'));
  const title = node('h2', '', 'Has construido y comprobado tu respuesta.'); title.tabIndex = -1; box.append(title);
  box.append(node('p', '', 'Identificaste el problema, elegiste el procedimiento y verificaste tus cálculos. Puedes volver a practicar con otros datos.'));
  if (state.results) {
    box.append(givenValues({given: state.results}));
    box.append(node('p', 'result-verdict', state.verdict));
  }
  const actions = node('div', 'activity-actions');
  actions.append(link(state.next_label || 'Explorar el cálculo completo →', state.next_url, 'btn btn-primary'));
  const again = node('button', 'btn btn-light', 'Practicar con otros datos'); again.addEventListener('click', () => begin(state.topic)); actions.append(again); box.append(actions);
  if (state.source) {
    // Las fuentes se abren al terminar: salir de la página durante la práctica la bloquea.
    const source = node('p', 'practice-source', 'Fundamento: ');
    const reference = link(`${state.source.title} ↗`, state.source.url, '');
    reference.target = '_blank'; reference.rel = 'noopener noreferrer'; source.append(reference); box.append(source);
  }
  box.append(node('p', 'activity-footnote', 'Este resultado se conserva en tu sesión del navegador.'));
  const choose = node('button', 'quiet-button', 'Elegir otra práctica');
  choose.addEventListener('click', () => {start.hidden = false; work.hidden = true; error.hidden = true; start.querySelector('button')?.focus();});
  box.append(choose);
  work.append(box); if (focus) title.focus();
}

const initial = await request({action: 'resume'});
if (initial && !initial.empty && (!filter || filter.id === 'practice-skill' || filter.value === 'all' || filter.value === initial.topic)) render(initial);
