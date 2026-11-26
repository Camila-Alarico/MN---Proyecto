// Página de lección del temario: laboratorio, preguntas con respuesta inmediata y avance.
const feedback = () => window.NumLearnFeedback;
const tabs = document.querySelector('[data-method-tabs]');

// Enlaces «Ver ejercicio» / «Probar en el laboratorio»: activan la pestaña correspondiente.
document.querySelectorAll('[data-jump]').forEach(link => link.addEventListener('click', event => {
  const tab = tabs?.querySelector(`[data-panel="${link.dataset.jump}"]`);
  if (!tab) return;
  event.preventDefault();
  tab.click();
  tabs.scrollIntoView({block: 'start', behavior: 'smooth'});
}));

// El laboratorio se monta cuando su panel se muestra por primera vez (las gráficas necesitan tamaño real).
const lab = document.querySelector('[data-lab]');
let mounted = false;
async function mountWhenVisible() {
  if (mounted || !lab || lab.closest('[hidden]')) return;
  mounted = true;
  try { (await import('./labs/index.js')).mount(lab); }
  catch (error) { console.error(error); lab.textContent = 'No se pudo cargar el laboratorio. Recarga la página.'; }
}
addEventListener('resize', mountWhenVisible);
addEventListener('hashchange', mountWhenVisible);
mountWhenVisible();

// Comprueba: cada pregunta responde al instante.
const quiz = document.querySelector('[data-quick-check]');
if (quiz) {
  const cards = [...quiz.querySelectorAll('.check-card')];
  const score = document.getElementById('check-score');
  let answered = 0, right = 0;
  cards.forEach(card => {
    const correct = Number(card.dataset.answer);
    const options = [...card.querySelectorAll('.check-option')];
    const note = card.querySelector('.check-feedback');
    options.forEach(option => option.addEventListener('click', () => {
      const chosen = Number(option.dataset.index), ok = chosen === correct;
      options.forEach((item, index) => {
        item.disabled = true;
        item.classList.toggle('is-correct', index === correct);
        item.classList.toggle('is-wrong', index === chosen && !ok);
        item.classList.toggle('is-muted', index !== correct && index !== chosen);
        item.querySelector('.check-icon').className = `check-icon bi ${index === correct ? 'bi-check-circle-fill' : index === chosen ? 'bi-x-circle-fill' : ''}`;
      });
      card.classList.add(ok ? 'is-right' : 'is-missed');
      note.hidden = false;
      note.className = `check-feedback ${ok ? 'is-right' : 'is-missed'}`;
      note.textContent = `${ok ? '¡Correcto!' : 'Todavía no.'} ${note.dataset.why}`;
      answered++; right += ok;
      if (answered === cards.length) {
        score.hidden = false;
        score.textContent = right === cards.length ? `${right} de ${cards.length}: dominas la idea. Marca la lección como completada.`
          : `${right} de ${cards.length}. Repasa la teoría de las preguntas falladas y vuelve a intentarlo recargando la página.`;
        if (right === cards.length) feedback()?.toast('¡Todas correctas!', 'success');
      }
    }));
  });
}

// Marcar la lección como completada sin recargar la página.
const button = document.getElementById('complete-lesson');
button?.addEventListener('click', async () => {
  const completed = button.dataset.completed !== '1';
  button.disabled = true;
  try {
    const response = await fetch(button.dataset.endpoint, {method: 'POST', credentials: 'same-origin',
      headers: {'Content-Type': 'application/json', 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value},
      body: JSON.stringify({topic: button.dataset.topic, completed})});
    const result = await response.json();
    if (!response.ok || !result.success) throw new Error(result.error || 'No se pudo guardar el avance.');
    button.dataset.completed = completed ? '1' : '0';
    button.setAttribute('aria-pressed', String(completed));
    button.textContent = completed ? 'Marcar como pendiente' : 'Marcar como completada';
    button.className = `btn ${completed ? 'btn-light' : 'btn-primary'}`;
    const box = document.getElementById('complete-box');
    box.classList.toggle('is-done', completed);
    if (completed) { box.classList.remove('is-celebrating'); void box.offsetWidth; box.classList.add('is-celebrating'); }
    document.getElementById('complete-title').textContent = completed ? 'Lección completada' : '¿Terminaste esta lección?';
    document.getElementById('complete-text').textContent = `Unidad: ${result.unit_finished} de ${result.unit_total} contenidos completados.`;
    const chip = document.getElementById('completion-chip');
    chip.classList.toggle('is-done', completed);
    chip.querySelector('i').className = `bi ${completed ? 'bi-check-circle-fill' : 'bi-circle'}`;
    chip.querySelector('span').textContent = completed ? 'Completada' : 'En curso';
    const rail = document.querySelector('.unit-rail-item[aria-current]');
    rail?.classList.toggle('is-done', completed);
    const current = document.querySelector('.sidebar-unit[aria-current]');
    if (current) {
      current.querySelector('.sidebar-unit-count').textContent = `${result.unit_finished}/${result.unit_total}`;
      current.querySelector('.sidebar-unit-bar > span').style.width = `${result.unit_finished / result.unit_total * 100}%`;
    }
    feedback()?.toast(result.message, completed ? 'success' : 'info');
  } catch (error) {
    feedback()?.toast(error.message, 'error');
  } finally { button.disabled = false; }
});
