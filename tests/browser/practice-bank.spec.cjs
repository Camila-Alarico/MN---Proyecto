const {test, expect} = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;

test.beforeEach(async ({page}) => {
  await page.route(/^https:\/\//, route => route.abort());
});

test('el banco permite filtrar, mostrar más y llegar desde el método correspondiente', async ({page}, info) => {
  await page.goto('/ecuaciones-no-lineales/practica/?tema=all');
  await expect(page.locator('.exercise-card')).toHaveCount(54);
  await expect(page.locator('.exercise-card:visible')).toHaveCount(6);
  await page.getByRole('button', {name: 'Ver más ejercicios'}).click();
  await expect(page.locator('.exercise-card:visible')).toHaveCount(12);
  await page.locator('#practice-topic').selectOption('raices-multiples');
  await expect(page.locator('.exercise-card:visible')).toHaveCount(3);
  await expect(page.locator('#practice-count')).toContainText('3 de 3');
  await page.goto('/ecuaciones-no-lineales/regla-falsa/');
  await page.getByRole('link', {name: 'Practicar →', exact: true}).click();
  await expect(page.locator('#practice-topic')).toHaveValue('regla-falsa');
  await expect(page.locator('.exercise-card:visible')).toHaveCount(6);
  await page.screenshot({path: info.outputPath('banco-regla-falsa.png'), fullPage: true});
});

for (const slug of ['biseccion', 'regla-falsa', 'punto-fijo', 'newton', 'secante', 'raices-multiples']) {
  test(`la calculadora conserva todos sus controles y resuelve ${slug}`, async ({page}) => {
    await page.goto(`/ecuaciones-no-lineales/${slug}/#simulator`);
    for (const id of ['method-select', 'expression', 'tolerance', 'max_iterations', 'example', 'execute', 'reset', 'copy-link', 'previous', 'next', 'auto', 'iteration-slider', 'export-csv', 'range-min', 'range-max', 'y-min', 'y-max', 'convergence-plot']) {
      await expect(page.locator(`#${id}`)).toHaveCount(1);
    }
    const response = page.waitForResponse(r => /\/api\/nonlinear\/[^/]+\/$/.test(r.url()) && !r.url().endsWith('/graph/'));
    await page.locator('#execute').click();
    expect((await response).status()).toBe(200);
    await expect(page.locator('#state')).toHaveText('Convergió');
    await expect(page.locator('#iterations table tbody tr')).not.toHaveCount(0);
    await expect(page.locator('#export-csv')).toBeEnabled();
    await expect(page.locator('#alert')).toBeHidden();
  });
}

test('reproducción, rango, CSV, enlace, ejemplos y reinicio mantienen su comportamiento', async ({page}, info) => {
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'clipboard', {value: {writeText: async text => {window.copiedConfiguration = text;}}});
  });
  await page.goto('/ecuaciones-no-lineales/newton/#simulator');
  await page.locator('#next').click();
  await expect(page.locator('#iteration-count')).toContainText('1 /');
  await page.locator('#next').click();
  await expect(page.locator('#iteration-count')).toContainText('2 /');
  await page.locator('#previous').click();
  await expect(page.locator('#iteration-count')).toContainText('1 /');
  await page.locator('#auto').click();
  await expect(page.locator('#state')).toHaveText('Convergió');
  await page.locator('#iteration-slider').fill('0');
  await expect(page.locator('#iteration-count')).toContainText('1 /');
  const summary = await page.locator('#result-summary').textContent();
  await page.locator('.graph-controls summary').click();
  await page.locator('#range-min').fill('1'); await page.locator('#range-max').fill('2');
  await page.locator('#y-min').fill('-1'); await page.locator('#y-max').fill('1');
  const graphResponse = page.waitForResponse(r => r.url().endsWith('/api/nonlinear/graph/'));
  await page.getByRole('button', {name: 'Aplicar rango'}).click();
  expect((await graphResponse).status()).toBe(200);
  await expect(page.locator('#result-summary')).toHaveText(summary);
  const download = page.waitForEvent('download');
  await page.locator('#export-csv').click();
  expect((await download).suggestedFilename()).toMatch(/^numlearn-newton-.*\.csv$/);
  await page.locator('#copy-link').click();
  await expect(page.locator('#copy-feedback')).toContainText('Enlace copiado');
  const copied = new URL(await page.evaluate(() => window.copiedConfiguration));
  expect(copied.searchParams.get('expression')).toBe('x^3 - x - 2');
  await page.locator('#example').selectOption('1');
  await expect(page.locator('#iteration-count')).toHaveText('0 pasos');
  await page.locator('#execute').click();
  await expect(page.locator('#result-summary')).toContainText('0.739');
  await expect(page.locator('#derivatives mjx-container')).toHaveCount(1);
  const a11y = await new AxeBuilder({page}).withTags(['wcag2a', 'wcag2aa', 'wcag21aa']).analyze();
  expect(a11y.violations.map(v => ({id: v.id, nodes: v.nodes.map(n => n.target)}))).toEqual([]);
  await page.locator('#reset').click();
  await expect(page.locator('#expression')).toHaveValue('x^3 - x - 2');
  await expect(page.locator('#iteration-count')).toHaveText('0 pasos');
  for (const width of [1440, 1024, 390]) {
    await page.setViewportSize({width, height: 1000});
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    await page.screenshot({path: info.outputPath(`calculadora-${width}.png`), fullPage: true});
  }
});

test('punto fijo y raíces múltiples muestran fórmulas y gráficas propias', async ({page}) => {
  for (const [topic, method] of [['punto-fijo', 'fixed-point'], ['raices-multiples', 'multiple-roots']]) {
    await page.goto(`/ecuaciones-no-lineales/practica/?tema=${topic}`);
    await page.locator(`[data-exercise="${topic}-1"]`).click();
    for (const choice of ['root', method]) {
      await page.locator(`[name="choice"][value="${choice}"]`).check();
      await page.getByRole('button', {name: 'Comprobar respuesta', exact: true}).click();
      await page.getByRole('button', {name: 'Continuar →'}).click();
    }
    await expect(page.locator('.practice-graph svg')).toBeVisible();
    if (topic === 'punto-fijo') await expect(page.locator('.practice-graph figcaption')).toContainText('diagonal');
    await page.locator('[name="x0"]').fill(topic === 'punto-fijo' ? '1.5' : '2.5');
    await page.getByRole('button', {name: 'Comprobar respuesta', exact: true}).click();
    await page.getByRole('button', {name: 'Continuar →'}).click();
    await expect(page.locator('.reference-formula mjx-container')).toHaveCount(topic === 'punto-fijo' ? 2 : 4);
    await expect(page.locator('mjx-merror')).toHaveCount(0);
  }
});
