const {test, expect} = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;

test.beforeEach(async ({page}) => {
  await page.route(/^https:\/\//, route => route.abort());
});

test('el menú lateral se oculta, aparece desde el borde izquierdo y se fija con el dardo', async ({page}) => {
  await page.goto('/ecuaciones-no-lineales/errores/');
  const sidebar = page.locator('#sidebar');
  await expect.poll(() => sidebar.evaluate(el => el.getBoundingClientRect().right)).toBeLessThanOrEqual(0);
  expect(await page.locator('.workspace').evaluate(el => parseFloat(getComputedStyle(el).marginLeft))).toBe(0);
  await page.mouse.move(400, 400);
  await page.mouse.move(4, 400, {steps: 6});
  await expect(sidebar).toHaveClass(/is-peeking/);
  await expect.poll(() => sidebar.evaluate(el => el.getBoundingClientRect().left)).toBeGreaterThanOrEqual(0);
  const pin = page.getByRole('button', {name: 'Fijar menú lateral'});
  await pin.click();
  await expect(page.getByRole('button', {name: 'Desfijar menú lateral'})).toHaveAttribute('aria-pressed', 'true');
  await page.mouse.move(900, 500, {steps: 4});
  await page.reload();
  await expect(page.locator('html')).toHaveClass(/sidebar-pinned/);
  await expect.poll(() => page.locator('.workspace').evaluate(el => parseFloat(getComputedStyle(el).marginLeft))).toBeGreaterThan(100);
  await page.getByRole('button', {name: 'Desfijar menú lateral'}).click();
  await page.mouse.move(900, 500, {steps: 4});
  await expect(sidebar).not.toHaveClass(/is-peeking/);
  expect(await page.evaluate(() => localStorage.getItem('numlearn:sidebar-pinned'))).toBe('0');
});

test('la animación del ejercicio resuelto avanza paso a paso y en automático', async ({page}) => {
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto('/ecuaciones-no-lineales/biseccion/#ejercicio-resuelto');
  const root = page.getByTestId('theory-animation-bisection');
  await root.getByRole('button', {name: 'Iniciar animación'}).click();
  await expect(root.getByTestId('anim-counter')).toHaveText(/Paso 1 de 6/i);
  await expect(root.getByRole('button', {name: 'Paso a paso'})).toHaveAttribute('aria-pressed', 'true');
  await root.getByTestId('anim-next').click();
  await expect(root.getByTestId('anim-counter')).toHaveText(/Paso 2 de 6/i);
  await expect(page.locator('#ejercicio-resuelto tbody tr').first()).toHaveClass(/anim-highlight/);
  await expect(page.locator('.worked-list li').nth(1)).toHaveClass(/anim-highlight/);
  await root.getByTestId('anim-prev').click();
  await expect(root.getByTestId('anim-counter')).toHaveText(/Paso 1 de 6/i);
  await root.getByRole('button', {name: 'Automático'}).click();
  await root.getByRole('button', {name: 'Rápido'}).click();
  await expect(root.getByTestId('anim-play')).toContainText('Pausar');
  await expect(root.getByTestId('anim-counter')).toHaveText(/Paso 3 de 6/i, {timeout: 6000});
  await root.getByTestId('anim-play').click();
  await expect(root.getByTestId('anim-play')).toContainText('Reproducir');
  const accessibility = await new AxeBuilder({page}).include('[data-testid=theory-animation-bisection]').withTags(['wcag2a', 'wcag2aa']).analyze();
  expect(accessibility.violations.map(item => item.id)).toEqual([]);
  await root.getByRole('button', {name: 'Cerrar animación'}).click();
  await expect(root.getByRole('button', {name: 'Iniciar animación'})).toBeFocused();
  expect(errors).toEqual([]);
});

test('los temas de teoría animan errores y sistemas lineales', async ({page}) => {
  await page.goto('/ecuaciones-no-lineales/errores/');
  const errorsScene = page.getByTestId('theory-animation-errors');
  await errorsScene.getByRole('button', {name: 'Iniciar animación'}).click();
  for (let i = 0; i < 5; i++) await errorsScene.getByTestId('anim-next').click();
  await expect(errorsScene.getByTestId('anim-caption-title')).toContainText('no cumple');
  await page.goto('/sistemas-lineales/formulacion/');
  const seidel = page.getByTestId('theory-animation-seidel');
  await seidel.getByRole('button', {name: 'Iniciar animación'}).click();
  await seidel.getByTestId('anim-dot-7').click();
  await expect(seidel.getByTestId('anim-caption-title')).toContainText('Iteración 8');
});
