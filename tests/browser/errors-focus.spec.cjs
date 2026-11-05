const {test, expect} = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;

test.beforeEach(async ({page}) => {
  await page.route(/^https:\/\//, route => route.abort());
});

async function answer(page, values) {
  for (const [name, value] of Object.entries(values)) {
    const input = page.locator(`[name="${name}"]`);
    if (name === 'choice') await page.locator(`[name="choice"][value="${value}"]`).check();
    else if (await input.evaluate(el => el.tagName === 'SELECT')) await input.selectOption(value);
    else await input.fill(String(value));
  }
  const response = page.waitForResponse(r => r.url().includes('/api/nonlinear/learning/') && r.request().postDataJSON().action === 'check');
  await page.getByRole('button', {name: 'Comprobar respuesta', exact: true}).click();
  return (await response).json();
}
async function advance(page, values) {
  expect((await answer(page, values)).correct).toBe(true);
  await page.getByRole('button', {name: /Continuar →|Ver resultado →/}).click();
}

test('el recorrido principal mantiene errores y deja los otros temas como complemento', async ({page}, info) => {
  await page.goto('/');
  await expect(page.locator('.sidebar-course')).toContainText('Errores numéricos');
  await expect(page.locator('.study-home')).toContainText('ERRORES NUMÉRICOS');
  await expect(page.locator('.home-paths')).not.toContainText('Newton');
  await expect(page.locator('.secondary-topics')).not.toHaveAttribute('open', '');
  await page.getByRole('link', {name: /Empezar por la teoría/}).click();
  await expect(page).toHaveURL(/\/errores\/$/);
  await expect(page.getByRole('tab')).toHaveCount(3);
  await expect(page.locator('#fundamento')).toBeVisible();
  await expect(page.locator('#aplicacion')).toBeHidden();
  await page.getByRole('tab', {name: 'Origen del error'}).click();
  await expect(page.locator('#tipos')).toBeVisible();
  await expect(page.locator('#fundamento')).toBeHidden();
  await page.screenshot({path: info.outputPath('errores-origen.png'), fullPage: true});
  await page.getByRole('tab', {name: 'Explorador'}).click();
  await expect(page.locator('#errors-form')).toBeVisible();
  for (const id of ['error-example', 'true-value', 'approximate-value', 'error-tolerance', 'approximation-slider', 'try-boundary', 'display-decimals']) await expect(page.locator(`#${id}`)).toBeVisible();
});

test('la práctica principal tiene quince ejercicios contextualizados de errores y filtros del mismo tema', async ({page}, info) => {
  await page.goto('/ecuaciones-no-lineales/practica/');
  await expect(page.locator('.exercise-card')).toHaveCount(15);
  await expect(page.locator('[data-start-topic]:not([data-start-topic="errores"])')).toHaveCount(0);
  await page.getByRole('button', {name: 'Ver más ejercicios'}).click();
  await expect(page.locator('.exercise-card:visible')).toHaveCount(12);
  await page.locator('#practice-skill').selectOption('representacion');
  await expect(page.locator('.exercise-card:visible')).toHaveCount(2);
  await expect(page.locator('.exercise-cards')).toContainText('π redondeado para un engrane');
  await page.locator('#practice-skill').selectOption('limites');
  await expect(page.locator('[data-exercise="errores-9"]')).toBeVisible();
  for (const width of [1440, 390]) {
    await page.setViewportSize({width, height: 1000});
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    await page.screenshot({path: info.outputPath(`practica-errores-${width}.png`), fullPage: true});
  }
});

test('referencia cero se resuelve sin confundir no definido con cero', async ({page}, info) => {
  await page.goto('/ecuaciones-no-lineales/practica/?grupo=limites');
  await page.locator('[data-exercise="errores-9"]').click();
  await advance(page, {choice: 'error'}); await advance(page, {choice: 'absolute'});
  await advance(page, {v: 0, approx: .0002}); await advance(page, {x: .0002});
  const incorrect = await answer(page, {relative: 'zero', percentage: 'undefined', decision: 'no'});
  expect(incorrect.correct).toBe(false);
  await expect(page.locator('#check-relative')).toContainText('dividir entre cero');
  await expect(page.locator('[name="percentage"]')).toHaveValue('undefined');
  await expect(page.locator('mjx-merror')).toHaveCount(0);
  const accessibility = await new AxeBuilder({page}).withTags(['wcag2a', 'wcag2aa', 'wcag21aa']).analyze();
  expect(accessibility.violations.map(v => ({id: v.id, nodes: v.nodes.map(n => n.target)}))).toEqual([]);
  await advance(page, {relative: 'undefined', percentage: 'undefined', decision: 'no'});
  await expect(page.locator('.activity-result')).toContainText('No cumple la tolerancia');
  await expect(page.locator('.activity-result .practice-given')).toContainText('no definido');
  await expect(page.getByRole('link', {name: 'Comprobar conceptos →'})).toHaveAttribute('href', '/ecuaciones-no-lineales/autoevaluacion/');
  await page.screenshot({path: info.outputPath('referencia-cero-resultado.png'), fullPage: true});
});

test('la evaluación de errores presenta conceptos, explicación y problema paso a paso en ese orden', async ({page}) => {
  await page.goto('/ecuaciones-no-lineales/autoevaluacion/');
  await expect(page.locator('input[name="scope"][value="errores"]')).toBeChecked();
  await page.locator('#student-name').fill('Alumno de prueba');
  await page.getByRole('button', {name: /Empezar autoevaluación/}).click();
  const phases = [];
  for (let i = 0; i < 10; i++) {
    await expect(page.locator('.activity-top')).toContainText(`Pregunta ${i + 1} de 10`);
    phases.push((await page.locator('.activity-top .eyebrow').innerText()).split(' · ')[1]);
    if (phases[i] === 'Conceptos') {
      expect(await page.locator('.multi-options input[type=checkbox]').count()).toBeGreaterThanOrEqual(5);
      await page.locator('.multi-options input').first().check();
      await page.getByRole('button', {name: 'Comprobar respuesta'}).click();
    } else if (phases[i] === 'Explicación') {
      await page.locator('textarea').fill('Explico el procedimiento con calma porque necesito justificar cada decisión que tomo. '.repeat(3));
      await page.getByRole('button', {name: 'Enviar respuesta'}).click();
    } else {
      await expect(page.locator('.stepper li.is-locked').first()).toContainText('Se desbloquea');
      // Con respuestas erróneas cada paso se revela tras tres intentos; así se recorre el problema sin conocer las respuestas.
      for (let guard = 0; guard < 40 && await page.getByText('Problema completado.').count() === 0; guard++) {
        const number = page.locator('#step-number');
        if (await number.count()) await number.fill('-987654'); else await page.locator('.step-choices input').last().check();
        await Promise.all([
          page.waitForResponse(r => r.url().includes('/evaluacion/api/') && r.request().postDataJSON()?.action === 'answer'),
          page.getByRole('button', {name: 'Comprobar paso'}).click(),
        ]);
        await page.waitForTimeout(150);  // deja que el navegador vuelva a dibujar el paso
      }
    }
    await page.getByRole('button', {name: /Continuar →|Ver resultado →/}).click();
  }
  expect(phases.slice(0, 4)).toEqual(Array(4).fill('Conceptos'));
  expect(phases.slice(4, 7)).toEqual(Array(3).fill('Explicación'));
  expect(phases.slice(7)).toEqual(Array(3).fill('Problema paso a paso'));
});

test('el explorador respeta la igualdad decimal y mantiene sus controles', async ({page}) => {
  await page.goto('/ecuaciones-no-lineales/errores/#aplicacion');
  await page.locator('#true-value').fill('1');
  await page.locator('#approximate-value').fill('1.1');
  await page.locator('#error-tolerance').fill('.1');
  await expect(page.locator('#tolerance-feedback')).toHaveAttribute('data-outcome', 'accepted');
  await expect(page.locator('#absolute')).toHaveText('0.1');
  await page.locator('#approximate-value').fill('1.100001');
  await expect(page.locator('#tolerance-feedback')).toHaveAttribute('data-outcome', 'rejected');
  await page.locator('#try-boundary').click();
  await expect(page.locator('#approximate-value')).toHaveValue('1.1');
  await expect(page.locator('#tolerance-feedback')).toHaveAttribute('data-outcome', 'accepted');
  await page.locator('#display-decimals').fill('8');
  await expect(page.locator('#absolute')).toHaveText('0.1');
  await page.locator('#error-example').selectOption('zero');
  await expect(page.locator('#relative')).toHaveText('No definido');
  await expect(page.locator('#error-worked mjx-container')).toHaveCount(1);
});
