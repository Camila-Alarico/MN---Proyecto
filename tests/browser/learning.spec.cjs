const {test, expect} = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;

test.beforeEach(async ({page}) => {
  await page.route(/^https:\/\//, route => route.abort());
});

async function startPractice(page, topic) {
  await page.goto(`/ecuaciones-no-lineales/practica/?tema=${topic}`);
  const response = page.waitForResponse(r => r.url().endsWith('/api/nonlinear/learning/practice/') && r.request().postDataJSON().action === 'start');
  await page.locator(`[data-exercise="${topic}-0"]`).click();
  return (await response).json();
}
async function check(page, data) {
  for (const [key, value] of Object.entries(data)) {
    const input = page.locator(`[name="${key}"]`);
    if (key === 'choice') await page.locator(`[name="choice"][value="${value}"]`).check();
    else if (key === 'decision') await input.selectOption(value);
    else await input.fill(String(value));
  }
  const response = page.waitForResponse(r => r.url().includes('/api/nonlinear/learning/') && r.request().postDataJSON().action === 'check');
  await page.getByRole('button', {name: 'Comprobar respuesta', exact: true}).click();
  return (await response).json();
}
async function next(page) {
  await page.getByRole('button', {name: /Continuar|Ver resultado/}).click();
}
async function choose(page, choice) {
  const answer = await check(page, {choice}); expect(answer.correct).toBe(true); await next(page); return answer;
}

test('inicio muestra tres actividades y el espacio personal queda cerrado', async ({page}, info) => {
  await page.goto('/');
  await expect(page.locator('.primary-learning a')).toHaveCount(5);
  await expect(page.locator('.primary-learning')).not.toContainText('Mi progreso');
  await expect(page.getByRole('link', {name: 'Mis apuntes', exact: true})).toBeHidden();
  await expect(page.locator('.home-paths')).toContainText('Práctica guiada');
  await expect(page.locator('.home-paths')).toContainText('Autoevaluación');
  await page.screenshot({path: info.outputPath('inicio-escritorio.png'), fullPage: true});
});

test('la teoría conserva seis temas y enlaces a todos los métodos', async ({page}) => {
  await page.goto('/ecuaciones-no-lineales/teoria/?vista=modulo');
  await expect(page.locator('.study-topic')).toHaveCount(6);
  await expect(page.locator('.topic-strip a')).toHaveCount(6);
  await expect(page.getByRole('link', {name: 'Newton-Raphson', exact: true})).toBeVisible();
});

test('las pestañas separan teoría, ejemplo y calculadora, con teclado y enlaces reproducibles', async ({page}) => {
  await page.goto('/ecuaciones-no-lineales/newton/');
  await expect(page.locator('#theory')).toBeVisible();
  await expect(page.locator('#simulator')).toBeHidden();
  const theory = page.getByRole('tab', {name: 'Teoría', exact: true});
  await theory.focus(); await page.keyboard.press('ArrowRight');
  await expect(page.getByRole('tab', {name: 'Ejercicio resuelto'})).toBeFocused();
  await expect(page.locator('#ejercicio-resuelto')).toBeVisible();
  await expect(page.locator('#theory')).toBeHidden();
  await page.getByRole('link', {name: /Reproducir en el simulador/}).click();
  await expect(page.locator('#simulator')).toBeVisible();
  await expect(page.locator('#x0')).toHaveValue('1.5');
});

test('bisección comprueba la elección, la gráfica y el cálculo del estudiante', async ({page}, info) => {
  const state = await startPractice(page, 'biseccion');
  const c = Number(state.expression.split('-')[1]);
  await choose(page, 'root');
  await expect(page.locator('.practice-graph svg')).toBeVisible();
  const wrong = await check(page, {choice: 'newton'});
  expect(wrong.correct).toBe(false);
  await expect(page.locator('.activity-form .activity-feedback')).toContainText('punto medio');
  await choose(page, 'bisection');
  await expect(page.locator('.practice-graph svg')).toBeVisible();
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({path: info.outputPath('practica-grafica.png'), fullPage: true});
  expect((await check(page, {a: 0, b: 3})).correct).toBe(true); await next(page);
  expect((await check(page, {x: 1.5})).correct).toBe(true); await next(page);
  expect((await check(page, {bound: 1.5, residual: Math.abs(2.25-c)})).correct).toBe(true); await next(page);
  await expect(page.getByRole('heading', {name: 'Has construido y comprobado tu respuesta.'})).toBeVisible();
  const target = new URL(await page.getByRole('link', {name: /Explorar el cálculo completo/}).getAttribute('href'), 'http://localhost');
  expect(Number(target.searchParams.get('a'))).toBe(0);
  expect(Number(target.searchParams.get('b'))).toBe(3);
});

test('Newton explica la derivada nula y comprueba paso y residuo', async ({page}) => {
  const state = await startPractice(page, 'newton');
  const c = Number(state.expression.split('-')[1]);
  await choose(page, 'root'); await choose(page, 'newton');
  expect((await check(page, {x0: 0})).correct).toBe(false);
  await expect(page.locator('.activity-form .activity-feedback')).toContainText('derivada');
  expect((await check(page, {x0: 2})).correct).toBe(true); await next(page);
  const x = 1+c/4;
  expect((await check(page, {x})).correct).toBe(true); await next(page);
  expect((await check(page, {bound: Math.abs(x-2), residual: Math.abs(x*x-c)})).correct).toBe(true); await next(page);
  await expect(page.locator('.activity-result')).toBeVisible();
});

test('errores incluye interpretar la tolerancia además de calcular', async ({page}) => {
  const state = await startPractice(page, 'errores');
  // Los datos numéricos viajan en math_context; el enunciado (state.problem) ahora es una situación contextualizada.
  const [v, approx, tolerance] = state.math_context.given.map(item => Number(item.fallback.split('=')[1]));
  expect(state.problem.split(' ').length).toBeGreaterThan(18);
  await choose(page, 'error'); await choose(page, 'absolute');
  expect((await check(page, {v, approx})).correct).toBe(true); await next(page);
  const ea = Math.abs(v-approx), relative = ea/Math.abs(v);
  expect((await check(page, {x: ea})).correct).toBe(true); await next(page);
  expect((await check(page, {relative, percentage: 100*relative, decision: ea <= tolerance ? 'yes' : 'no'})).correct).toBe(true); await next(page);
  await expect(page.locator('.activity-result')).toBeVisible();
});

test('recargar durante la práctica la bloquea y obliga a repetirla desde el inicio', async ({page}) => {
  await startPractice(page, 'biseccion');
  await choose(page, 'root');
  await page.reload();
  await expect(page.locator('.activity-locked h2')).toContainText('se bloqueó');
  await expect(page.locator('.activity-locked')).toContainText('repetirla desde el inicio');
  await page.reload();                        // volver a cargar no recupera el avance
  await expect(page.locator('.activity-locked')).toBeVisible();
  await page.getByRole('button', {name: 'Repetir desde el inicio'}).click();
  await expect(page.locator('.activity-top')).toContainText('Paso 1 de 5');
});

test('salir de la pestaña bloquea la práctica y al volver se muestra el aviso', async ({page}) => {
  await startPractice(page, 'errores');
  await choose(page, 'error');
  await page.evaluate(() => { Object.defineProperty(document, 'hidden', {configurable: true, get: () => true}); document.dispatchEvent(new Event('visibilitychange')); });
  await page.evaluate(() => { Object.defineProperty(document, 'hidden', {configurable: true, get: () => false}); document.hasFocus = () => true; document.dispatchEvent(new Event('visibilitychange')); });
  await expect(page.locator('.activity-locked')).toContainText('Saliste de la página');
  await expect(page.getByRole('button', {name: 'Elegir otra práctica'})).toBeVisible();
  await page.getByRole('button', {name: 'Repetir desde el inicio'}).click();
  await expect(page.locator('.activity-top')).toContainText('Paso 1 de 5');
});

test('autoevaluación mezcla formatos, no permite repetir y registra la salida de la pestaña', async ({page}) => {
  const events = [];
  page.on('request', r => { const d = r.method() === 'POST' && r.url().includes('/evaluacion/api/') ? r.postDataJSON() : null; if (d?.action === 'event') events.push(d.kind); });
  await page.goto('/ecuaciones-no-lineales/autoevaluacion/');
  await page.locator('#student-name').fill('Alumno de prueba');
  await page.getByRole('button', {name: /Empezar autoevaluación/}).click();
  await expect(page.locator('.activity-top')).toContainText('Pregunta 1 de 10');
  expect(await page.locator('.multi-options input[type=checkbox]').count()).toBeGreaterThanOrEqual(5);
  await page.evaluate(() => { Object.defineProperty(document, 'hidden', {configurable: true, get: () => true}); document.dispatchEvent(new Event('visibilitychange')); });
  await page.evaluate(() => { Object.defineProperty(document, 'hidden', {configurable: true, get: () => false}); document.hasFocus = () => true; document.dispatchEvent(new Event('visibilitychange')); });
  await expect(page.locator('.assess-banner')).toContainText('Se registró que saliste');
  await expect.poll(() => events).toEqual(expect.arrayContaining(['leave', 'return']));
  await page.locator('.multi-options input').first().check();
  await page.getByRole('button', {name: 'Comprobar respuesta'}).click();
  await expect(page.locator('.multi-options input').first()).toBeDisabled();
  await page.getByRole('button', {name: /Continuar →/}).click();
  await expect(page.locator('.activity-top')).toContainText('Pregunta 2 de 10');
});

test('el botón Teoría lleva al índice general del curso', async ({page}) => {
  for (const path of ['/ecuaciones-no-lineales/errores/', '/sistemas-lineales/gauss-seidel/']) {
    await page.goto(path);
    await page.locator('#sidebar').getByRole('link', {name: /Teoría/}).first().click();
    await expect(page).toHaveURL(/\/teoria\/$/);
    await expect(page.getByRole('heading', {name: 'Sistemas de ecuaciones lineales'})).toBeVisible();
  }
});

test('móvil permite cerrar el menú con Escape y no desborda horizontalmente', async ({page}, info) => {
  await page.setViewportSize({width: 390, height: 844});
  await page.goto('/');
  const menu = page.getByRole('button', {name: 'Abrir menú', exact: true});
  await menu.click();
  await expect(page.locator('#sidebar')).toHaveClass(/open/);
  expect(await page.locator('.workspace').evaluate(el => el.inert)).toBe(true);
  await page.keyboard.press('Escape');
  await expect(menu).toBeFocused();
  await expect(page.locator('#sidebar')).not.toHaveClass(/open/);
  await menu.click();
  await page.locator('#sidebar').getByRole('link', {name: 'Programa del curso', exact: true}).click();
  await expect(page.locator('#sidebar')).not.toHaveClass(/open/);
  await expect(page.locator('#modules')).toHaveAttribute('open', '');
  await page.goto('/ecuaciones-no-lineales/practica/');
  await expect(page.locator('[data-start-topic="errores"]').first()).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.screenshot({path: info.outputPath('practica-movil.png'), fullPage: true});
});

test('las páginas nuevas pasan comprobaciones básicas de accesibilidad', async ({page}) => {
  for (const path of ['/', '/ecuaciones-no-lineales/teoria/', '/ecuaciones-no-lineales/practica/', '/ecuaciones-no-lineales/autoevaluacion/']) {
    await page.goto(path);
    const result = await new AxeBuilder({page}).withTags(['wcag2a', 'wcag2aa', 'wcag21aa']).analyze();
    expect(result.violations.map(v => ({id: v.id, nodes: v.nodes.map(n => n.target)})), path).toEqual([]);
  }
});

test('errores muestra LaTeX local y corrige cada campo sin borrar los aciertos', async ({page}, info) => {
  const runtimeErrors = [];
  page.on('pageerror', error => runtimeErrors.push(error.message));
  const state = await startPractice(page, 'errores');
  // Los datos numéricos viajan en math_context; el enunciado (state.problem) ahora es una situación contextualizada.
  const [v, approx, tolerance] = state.math_context.given.map(item => Number(item.fallback.split('=')[1]));
  expect(state.problem.split(' ').length).toBeGreaterThan(18);
  await choose(page, 'error'); await choose(page, 'absolute');
  expect((await check(page, {v, approx})).correct).toBe(true); await next(page);
  const ea = Math.abs(v-approx), relative = Number((ea/Math.abs(v)).toPrecision(10));
  expect((await check(page, {x: ea})).correct).toBe(true); await next(page);
  await expect(page.locator('.practice-given mjx-container')).toHaveCount(3);
  await expect(page.locator('[data-field="relative"] .field-formula mjx-container')).toHaveCount(1);
  await expect(page.locator('mjx-merror')).toHaveCount(0);
  const decision = ea <= tolerance ? 'yes' : 'no';
  const wrong = await check(page, {relative: Number(ea.toPrecision(10)), percentage: .2, decision: decision === 'yes' ? 'no' : 'yes'});
  expect(wrong.correct).toBe(false);
  await expect(page.locator('[name="relative"]')).toHaveAttribute('aria-invalid', 'true');
  await expect(page.locator('#check-relative')).toContainText('repetido el error absoluto');
  await expect(page.locator('[name="percentage"]')).toHaveAttribute('aria-invalid', 'true');
  await expect(page.locator('[name="decision"]')).toHaveAttribute('aria-invalid', 'true');
  if (ea === tolerance) await expect(page.locator('#check-decision')).toContainText('igualdad');
  await expect(page.locator('#check-relative mjx-container')).toHaveCount(1);
  const accessibility = await new AxeBuilder({page}).withTags(['wcag2a', 'wcag2aa', 'wcag21aa']).analyze();
  expect(accessibility.violations.map(item => item.id)).toEqual([]);
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({path: info.outputPath('errores-latex-correccion.png'), fullPage: true, animations: 'disabled'});
  await page.setViewportSize({width: 390, height: 844});
  await expect.poll(() => page.locator('#sidebar').evaluate(element => element.getBoundingClientRect().right)).toBeLessThanOrEqual(0);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({path: info.outputPath('errores-latex-movil.png'), fullPage: true, animations: 'disabled'});
  await page.setViewportSize({width: 1440, height: 1000});
  const partial = await check(page, {relative, percentage: .2, decision});
  expect(partial.checks.map(item => item.correct)).toEqual([true, false, true]);
  await expect(page.locator('[name="relative"]')).toHaveAttribute('aria-invalid', 'false');
  await expect(page.locator('[name="relative"]')).toHaveValue(String(relative));
  expect((await check(page, {relative, percentage: 100*relative, decision})).correct).toBe(true);
  await next(page);
  await expect(page.locator('.activity-result .practice-given mjx-container')).toHaveCount(3);
  await expect(page.locator('.activity-result .result-verdict')).toHaveText(ea <= tolerance ? 'Cumple la tolerancia' : 'No cumple la tolerancia');
  expect(runtimeErrors).toEqual([]);
});

test('si falla el motor de fórmulas la práctica mantiene texto legible', async ({page}) => {
  await page.route('**/static/vendor/mathjax/**', route => route.abort());
  await startPractice(page, 'errores');
  await expect(page.locator('.practice-given')).toContainText('Tolerancia absoluta');
  await expect(page.locator('.given-value').first()).toContainText('v =');
  await expect(page.locator('.practice-given mjx-container')).toHaveCount(0);
  await choose(page, 'error');
  await expect(page.locator('.activity-top')).toContainText('Paso 2 de 5');
});

test('la lección de errores y el comparador conservan sus fórmulas dinámicas', async ({page}) => {
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto('/ecuaciones-no-lineales/errores/#aplicacion');
  await expect(page.locator('#error-worked mjx-container')).toHaveCount(1);
  await page.locator('#true-value').fill('20');
  await page.locator('#approximate-value').fill('19.5');
  await expect(page.locator('#absolute')).toHaveText('0.5');
  await expect(page.locator('#error-worked mjx-container')).toHaveCount(1);
  await expect(page.locator('mjx-merror')).toHaveCount(0);
  await page.goto('/ecuaciones-no-lineales/comparar/');
  await page.getByRole('button', {name: /Comparar recorridos/}).click();
  await expect(page.locator('#comparison-cards')).toContainText('Convergió');
  await expect(page.locator('#convergence-panels mjx-container')).toHaveCount(6);
  await expect(page.locator('mjx-merror')).toHaveCount(0);
  expect(errors).toEqual([]);
});
