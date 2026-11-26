const {test, expect} = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;

test.beforeEach(async ({page}) => {
  await page.route(/^https:\/\//, route => route.abort());
});

test('el curso tiene una sola entrada y las actividades pertenecen al tema elegido', async ({page}) => {
  await page.goto('/');
  await expect(page.locator('.primary-learning a')).toHaveCount(2);
  await expect(page.locator('.unit-block')).toHaveCount(6);
  await page.locator('#unidad-2').getByRole('link', {name: /^Bisección/}).click();
  await expect(page.locator('.course-location')).toContainText('Unidad 2');
  await page.getByRole('tab', {name: 'Calculadora', exact: true}).click();
  await expect(page.locator('#simulator')).toBeVisible();
  await page.getByRole('link', {name: 'Ejercicios guiados de Bisección', exact: true}).click();
  await expect(page.locator('#activity')).toHaveAttribute('data-topic', 'biseccion');
  await expect(page.locator('[data-exercise-topic]:visible').first()).toBeVisible();
  expect(await page.locator('[data-exercise-topic]').evaluateAll(cards => [...new Set(cards.map(c => c.dataset.exerciseTopic))])).toEqual(['biseccion']);
  await page.getByRole('link', {name: 'Volver a la lección de Bisección', exact: true}).click();
  await expect(page).toHaveURL(/\/biseccion\/$/);
});

test('la evaluación de raíces no mezcla el banco de errores', async ({page}) => {
  await page.goto('/');
  await page.getByRole('link', {name: 'Evaluar raíces de ecuaciones', exact: true}).click();
  await expect(page.locator('[name=scope]:checked')).toHaveValue('unidad-2');
  await expect(page.locator('#assess')).toHaveAttribute('data-scope', 'unidad-2');
});

test('el avance reúne temas antiguos y nuevos y persiste al recargar', async ({page}) => {
  await page.goto('/ecuaciones-no-lineales/newton/');
  await page.getByRole('button', {name: 'Marcar este tema como completado', exact: true}).click();
  await expect(page.getByText('Marcado como completado', {exact: true})).toBeVisible();
  await page.goto('/temario/serie-taylor/');
  await page.getByRole('tab', {name: 'Comprueba', exact: true}).click();
  await page.locator('#complete-lesson').click();
  await expect(page.locator('#complete-lesson')).toHaveAttribute('data-completed', '1');
  await page.goto('/avance/');
  await expect(page.locator('.study-heading')).toContainText('2 de');
  await page.reload();
  await expect(page.locator('.study-heading')).toContainText('2 de');
});

test('el curso y el avance funcionan en móvil con el menú y sin desbordarse', async ({page}, testInfo) => {
  await page.setViewportSize({width:390,height:844});
  await page.goto('/');
  await page.locator('#menu-toggle').click();
  await page.locator('.primary-learning').getByRole('link', {name:'Mi avance',exact:true}).click();
  await expect(page).toHaveURL(/\/avance\/$/);
  await expect(page.getByRole('heading', {name:'Tu recorrido por el curso'})).toBeVisible();
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  await page.goto('/');
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  await page.screenshot({path:testInfo.outputPath('curso-movil.png'),fullPage:true});
});

test('curso y avance pasan las comprobaciones básicas de accesibilidad', async ({page}, testInfo) => {
  for(const path of ['/','/avance/']) {
    await page.goto(path);
    const result=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa']).analyze();
    expect(result.violations).toEqual([]);
  }
  await page.goto('/');
  await page.screenshot({path:testInfo.outputPath('curso-escritorio.png'),fullPage:true});
});

test('la barra lateral muestra los nombres completos sin desplazamiento horizontal', async ({page}, testInfo) => {
  for(const width of [1440,390]) {
    await page.setViewportSize({width,height:960});
    await page.goto('/temario/integracion-numerica/');
    await page.locator('#menu-toggle').click();
    const sidebar=page.locator('#sidebar');
    await expect(sidebar).toBeVisible();
    await expect(sidebar.locator('.sidebar-unit-title')).toHaveCount(6);
    await expect(sidebar.locator('.sidebar-unit[aria-current]')).toContainText('Integración y derivación');
    expect(await sidebar.evaluate(el=>el.scrollWidth<=el.clientWidth)).toBe(true);
    const clipped=await sidebar.locator('.sidebar-unit-title').evaluateAll(labels=>labels.filter(el=>el.scrollWidth>el.clientWidth).map(el=>el.textContent));
    expect(clipped).toEqual([]);
    await sidebar.screenshot({path:testInfo.outputPath(`barra-${width}.png`)});
  }
});
