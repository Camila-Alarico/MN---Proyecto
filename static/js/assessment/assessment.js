import {post, busy} from '../nonlinear/common.js';

const root = document.getElementById('assess');
const endpoint = root.dataset.endpoint;
const startPanel = document.getElementById('assess-start');
const work = document.getElementById('assess-work');
const errorBox = document.getElementById('assess-error');
let attemptId = null;

function node(tag, className, text) {
  const item = document.createElement(tag);
  if (className) item.className = className;
  if (text !== undefined) item.textContent = text;
  return item;
}
const csrf = () => document.querySelector('[name=csrfmiddlewaretoken]').value;
function fail(message) {errorBox.textContent = message; errorBox.hidden = !message;}
async function call(payload) {
  fail('');
  try {return await post(endpoint, {attempt: attemptId, ...payload});}
  catch (error) {fail(error.message); return null;}
}

// --- Reinicio por salida prolongada ---------------------------------------------------------------
// Solo se guarda una marca temporal en la sesión para aplicar la regla de 5 segundos.
// No se envían eventos, duración ni información de salida a ningún panel docente.
let awaySince = null;
let leaveRequest = null;
let blurTimer = null;

function markAway(startedAt = Date.now()) {
  if (!attemptId || awaySince !== null) return;
  awaySince = startedAt;
  leaveRequest = fetch(endpoint, {
    method: 'POST',
    credentials: 'same-origin',
    keepalive: true,
    headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrf()},
    body: JSON.stringify({action: 'leave', attempt: attemptId}),
  }).catch(() => null);
}

async function markReturn() {
  if (awaySince === null || !attemptId) return;
  const elapsed = Date.now() - awaySince;
  awaySince = null;
  if (elapsed > 5000) {
    if (leaveRequest) await leaveRequest;
    const state = await call({action: 'restart'});
    leaveRequest = null;
    if (state) show(state, {restarted: true});
  } else {
    await post(endpoint, {action: 'return', attempt: attemptId}).catch(() => {});
    leaveRequest = null;
    if (!work.hidden && attemptId) {
      const banner = node('p', 'assess-banner assessment-return-notice', 'Regresaste antes de superar los 5 segundos. Tu avance se conservó.');
      work.prepend(banner);
    }
  }
}

document.addEventListener('visibilitychange', () => {
  if (document.hidden) markAway();
  else markReturn();
});
// Igual que la práctica guiada: una pérdida de foco breve se confirma tras 400 ms,
// pero el umbral que reinicia la autoevaluación sigue siendo estrictamente 5 segundos.
window.addEventListener('blur', () => {
  clearTimeout(blurTimer);
  blurTimer = setTimeout(() => {if (!document.hasFocus()) markAway(Date.now() - 400);}, 400);
});
window.addEventListener('focus', () => {
  clearTimeout(blurTimer);
  if (!document.hidden) markReturn();
});
window.addEventListener('pagehide', markAway);
window.addEventListener('pageshow', markReturn);

// --- Pantallas -------------------------------------------------------------------------------------
function show(state, {resumed = false, restarted = false} = {}) {
  work.replaceChildren(); startPanel.hidden = true; work.hidden = false;
  attemptId = state.attempt;
  if (state.scope) {
    const selectedScope = document.querySelector(`input[name="scope"][value="${state.scope}"]`);
    if (selectedScope) selectedScope.checked = true;
  }
  if (state.done) return renderFinal(state);
  if (restarted || state.restarted) {
    work.append(node('p', 'assess-banner assessment-away-notice', 'Saliste de la autoevaluación y permaneciste fuera más de 5 segundos. El intento anterior se reinició completamente; estás comenzando de nuevo en el mismo módulo.'));
  } else if (resumed) {
    work.append(node('p', 'assess-banner assessment-return-notice', 'Regresaste antes de superar los 5 segundos. Tu avance se conservó.'));
  }
  renderQuestion(state.question);
}

function header(q) {
  const top = node('div', 'activity-top');
  top.append(node('span', 'eyebrow', `Pregunta ${q.index + 1} · ${q.phase} · ${q.source.title}`));
  return [top];
}

function renderQuestion(q, note = null, outcome = null) {
  const keepBanners = [...work.querySelectorAll('.assess-banner')];
  work.replaceChildren(...keepBanners, ...header(q));
  const card = node('section', 'activity-card assess-card');
  const title = node('h2', '', q.type === 'steps' ? q.steps.intro : q.prompt); title.tabIndex = -1;
  card.append(title);
  if (q.type === 'multi') renderMulti(card, q, outcome);
  else if (q.type === 'open') renderOpen(card, q, outcome);
  else renderSteps(card, q, note, outcome);
  work.append(card);
  title.focus();
}

function footer(card, outcome, label = 'Continuar →') {
  const actions = node('div', 'activity-actions');
  const next = node('button', 'btn btn-primary', outcome.next.done ? 'Ver resultado →' : label); next.type = 'button';
  next.addEventListener('click', () => show(outcome.next));
  actions.append(next); card.append(actions); next.focus();
}

function feedbackBox(text, good) {
  const box = node('div', `activity-feedback ${good ? 'correct' : 'incorrect'}`, text);
  box.setAttribute('role', 'status'); box.tabIndex = -1; return box;
}

function renderMulti(card, q, outcome) {
  card.append(node('p', 'input-help', q.hint));
  const form = node('form', 'activity-form');
  const fieldset = node('fieldset', 'multi-options'); fieldset.append(node('legend', 'visually-hidden', 'Selecciona todas las respuestas correctas'));
  q.options.forEach((text, i) => {
    const label = node('label'); const box = node('input');
    Object.assign(box, {type: 'checkbox', value: String(i), name: 'option'});
    const mark = node('span', 'option-mark');
    if (outcome) {
      const detail = outcome.result.options[i]; box.disabled = true; box.checked = detail.chosen;
      label.classList.add(detail.correct ? (detail.chosen ? 'is-right' : 'is-missed') : (detail.chosen ? 'is-wrong' : 'x'));
      mark.textContent = detail.correct ? (detail.chosen ? '✓ correcta' : 'faltó marcarla') : (detail.chosen ? '✗ no corresponde' : '');
    }
    label.append(box, node('span', '', text), mark); fieldset.append(label);
  });
  form.append(fieldset);
  if (outcome) {card.append(form, feedbackBox(outcome.result.feedback, outcome.result.correct)); return footer(card, outcome);}
  const submit = node('button', 'btn btn-primary', 'Comprobar respuesta'); submit.type = 'submit';
  form.append(submit); card.append(form);
  form.addEventListener('submit', async event => {
    event.preventDefault();
    const selected = [...form.querySelectorAll('input:checked')].map(i => Number(i.value));
    if (!selected.length) return fail('Selecciona al menos una opción.');
    busy(submit, true, 'Comprobando…');
    const result = await call({action: 'answer', index: q.index, selected});
    busy(submit, false);
    if (result) renderQuestion(result.question, null, result);
  });
}

function renderOpen(card, q, outcome) {
  card.append(node('p', 'input-help', q.hint));
  const form = node('form', 'activity-form');
  const area = node('textarea'); Object.assign(area, {maxLength: q.max_chars, required: true, id: 'open-answer'});
  area.setAttribute('aria-label', 'Tu respuesta');
  const count = node('p', 'assess-count');
  const words = () => (area.value.match(/\p{L}[\p{L}\p{N}_']*|\p{N}+/gu) || []).length;
  const update = () => {count.textContent = `${words()} palabras (mínimo ${q.min_words}) · ${area.value.length}/${q.max_chars} caracteres`;};
  area.addEventListener('input', update); update();
  form.append(area, count); card.append(form);
  if (outcome) {
    area.value = area.value || ''; area.disabled = true;
    card.append(feedbackBox(outcome.result.feedback, outcome.result.correct));
    const detail = node('div', 'assess-detail');
    const list = node('ul');
    outcome.result.hits.forEach(t => list.append(node('li', 'hit', t)));
    outcome.result.missed.forEach(t => list.append(node('li', 'miss', t)));
    if (outcome.result.number_ok === false) list.append(node('li', 'miss', 'el valor numérico que se pedía no coincide con el de tu enunciado'));
    detail.append(node('strong', '', 'Elementos valorados'), list, node('p', '', outcome.result.review_note));
    const model = node('details'); model.append(node('summary', '', 'Ver una respuesta modelo'), node('p', '', outcome.result.model));
    detail.append(model); card.append(detail);
    return footer(card, outcome);
  }
  const submit = node('button', 'btn btn-primary', 'Enviar respuesta'); submit.type = 'submit'; form.append(submit);
  form.addEventListener('submit', async event => {
    event.preventDefault();
    busy(submit, true, 'Enviando…');
    const result = await call({action: 'answer', index: q.index, text: area.value});
    busy(submit, false);
    if (result) {const text = area.value; renderQuestion(result.question, null, result); const box = work.querySelector('textarea'); if (box) {box.value = text; box.dispatchEvent(new Event('input'));}}
  });
}

function renderSteps(card, q, note, outcome) {
  const data = q.steps;
  const given = node('ul', 'assess-given'); data.given.forEach(line => given.append(node('li', '', line))); card.append(given);
  if (note) card.append(feedbackBox(note.text, note.good));
  const list = node('ol', 'stepper');
  data.items.forEach(item => {
    const li = node('li', `is-${item.status}`);
    const head = node('div', 'step-label-line'); head.append(node('span', '', item.label));
    if (item.status === 'locked') {
      head.append(node('span', '', 'Se desbloquea al completar el paso anterior.')); li.setAttribute('aria-disabled', 'true'); li.append(head);
    } else {
      li.append(head, node('p', 'step-prompt', item.prompt));
      if (item.status === 'done') li.append(node('p', 'step-value', `${item.revealed ? '✗ Respuesta: ' : '✓ '}${item.shown}`));
      else li.append(stepForm(q, item, data.current));
    }
    list.append(li);
  });
  card.append(list);
  if (outcome?.result.question_done) card.append(feedbackBox('Problema completado.', true)), footer(card, outcome);
}

function stepForm(q, item, step) {
  const form = node('form', 'activity-form'); const fields = node('div', 'step-fields');
  let read;
  if (item.kind === 'choice') {
    const group = node('div', 'step-choices'); group.setAttribute('role', 'radiogroup');
    item.options.forEach(([value, label], i) => {
      const wrap = node('label'); const radio = node('input'); Object.assign(radio, {type: 'radio', name: 'step-choice', value, id: `step-${i}`});
      wrap.append(radio, document.createTextNode(' ' + label)); group.append(wrap);
    });
    fields.append(group); read = () => form.querySelector('input:checked')?.value ?? '';
  } else {
    const input = node('input'); Object.assign(input, {type: 'text', inputMode: 'decimal', autocomplete: 'off', required: true, id: 'step-number'});
    input.setAttribute('aria-label', 'Tu respuesta numérica');
    const wrap = node('div'); wrap.append(input); fields.append(wrap); read = () => input.value;
  }
  const submit = node('button', 'btn btn-primary', 'Comprobar paso'); submit.type = 'submit'; fields.append(submit);
  form.append(fields, node('p', 'input-help', `Intentos restantes en este paso: ${item.tries_left}. Usa punto decimal; si redondeas, conserva al menos 4 decimales.`));
  form.addEventListener('submit', async event => {
    event.preventDefault();
    const value = read();
    if (value === '') return fail('Escribe o elige una respuesta para este paso.');
    busy(submit, true, 'Comprobando…');
    const result = await call({action: 'answer', index: q.index, step, value});
    busy(submit, false);
    if (!result) return;
    const r = result.result;
    renderQuestion(result.question, {text: r.feedback, good: r.correct}, r.question_done ? result : null);
  });
  queueMicrotask(() => form.querySelector('input')?.focus());
  return form;
}

function renderFinal(state) {
  const card = node('section', 'activity-card assess-result');
  card.append(node('span', 'eyebrow', `RESULTADO · ${state.scope_title}`));
  const title = node('h2', '', state.passed ? 'Alcanzaste la meta de este intento' : 'Todavía hay temas por repasar'); title.tabIndex = -1; card.append(title);
  card.append(node('p', 'assess-score', `${state.percent} % de respuestas correctas`));
  card.append(node('p', '', `Meta de aprobación: ${state.pass_percent} %. Las preguntas abiertas se valoran mediante una rúbrica de conceptos.`));
  if (state.wrong) {
    const open = node('button', 'btn btn-light', `Ver solo las preguntas que fallé (${state.wrong})`); open.type = 'button';
    open.addEventListener('click', async () => {
      busy(open, true, 'Cargando…');
      const result = await call({action: 'review'});
      busy(open, false);
      if (result) renderReview(result, state);
    });
    card.append(open);
  } else card.append(node('p', 'assess-banner', 'No fallaste ninguna pregunta en este intento.'));
  const actions = node('div', 'activity-actions');
  const again = node('button', 'btn btn-primary', 'Elegir módulo / comenzar otro intento'); again.type = 'button';
  again.addEventListener('click', () => {attemptId = null; work.hidden = true; startPanel.hidden = false; fail(''); document.getElementById('start-assessment').focus();});
  const theory = node('a', 'btn btn-light', 'Ir a la teoría del curso'); theory.href = '/teoria/';
  actions.append(again, theory); card.append(actions); work.append(card); title.focus();
}


function renderReview(data, finalState) {
  work.replaceChildren();
  const head = node('section', 'activity-card');
  head.append(node('span', 'eyebrow', 'REVISIÓN · SOLO LO QUE FALLASTE'));
  const title = node('h2', '', `${data.wrong} respuestas para repasar`); title.tabIndex = -1; head.append(title);
  head.append(node('p', '', 'Cada tarjeta muestra tu respuesta, la respuesta correcta y la explicación. Las preguntas que acertaste no aparecen.'));
  const back = node('button', 'btn btn-light', '← Volver al resultado'); back.type = 'button';
  back.addEventListener('click', () => {work.replaceChildren(); renderFinal(finalState);});
  head.append(back); work.append(head);
  data.review.forEach(item => {
    const box = node('article', 'review-item');
    box.append(node('span', 'eyebrow', `Pregunta ${item.index} · ${item.phase} · ${item.topic}${item.subtopic ? ' · ' + item.subtopic : ''} · ${Math.round(item.score * 100)} %`));
    box.append(node('h3', '', item.prompt));
    if (item.type === 'multi') {
      item.options.forEach(option => {
        const row = node('div', `review-opt ${option.correct ? (option.chosen ? 'is-right' : 'is-missed') : (option.chosen ? 'is-wrong' : '')}`);
        row.append(node('span', '', option.correct ? (option.chosen ? '✓' : '○') : (option.chosen ? '✗' : '·')), node('span', '', option.text));
        if (option.correct && !option.chosen) row.append(node('em', '', 'faltó marcarla'));
        box.append(row);
      });
      box.append(node('p', 'input-help', item.explanation));
    } else if (item.type === 'open') {
      box.append(node('strong', '', 'Tu respuesta'), node('div', 'review-answer', item.answer));
      if (item.missed.length) {
        const list = node('ul'); item.missed.forEach(text => list.append(node('li', '', text)));
        box.append(node('strong', '', 'Elementos que faltaron'), list);
      }
      const model = node('details'); model.append(node('summary', '', 'Ver una respuesta modelo'), node('p', '', item.model)); box.append(model);
    } else {
      const given = node('ul', 'assess-given'); item.given.forEach(line => given.append(node('li', '', line))); box.append(given);
      const list = node('ol', 'stepper');
      item.steps.forEach(step => {
        const li = node('li', step.points >= 1 ? 'is-done' : 'is-current');
        li.append(node('p', 'step-prompt', step.prompt));
        li.append(node('p', '', `Tu respuesta: ${step.typed.length ? step.typed.join(' → ') : '—'}`));
        li.append(node('p', 'step-value', `Respuesta correcta: ${step.correct}${step.revealed ? ' (se mostró tras tres intentos)' : ''}`));
        if (step.points < 1) li.append(node('p', 'input-help', step.explain));
        list.append(li);
      });
      box.append(list);
    }
    const lesson = node('a', '', `Repasar: ${item.topic} →`); lesson.href = item.url; box.append(lesson);
    work.append(box);
  });
  title.focus();
}

// --- Arranque ----------------------------------------------------------------------------------------------
document.getElementById('start-assessment').addEventListener('click', async event => {
  const button = event.currentTarget;
  const scope = document.querySelector('input[name=scope]:checked')?.value;
  busy(button, true, 'Preparando…');
  const state = await call({action: 'start', scope});
  busy(button, false);
  if (state) show(state);
});

const resumed = await (async () => {
  try {return await post(endpoint, {action: 'resume', scope: root.dataset.scope});} catch {return null;}
})();
if (resumed && !resumed.empty) show(resumed, {resumed: Boolean(resumed.resumed)});
