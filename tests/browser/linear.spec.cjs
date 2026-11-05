const {test, expect} = require('@playwright/test');

test.beforeEach(async ({page}) => {
  // La calculadora debe seguir funcionando si las bibliotecas CDN no cargan.
  await page.route(/^https:\/\//, route => route.abort());
});

test('Gauss resuelve el caso base y muestra la verificación', async ({page}) => {
  await page.goto('/sistemas-lineales/eliminacion-gaussiana/');
  await page.getByRole('tab', {name: 'Calculadora', exact: true}).click();
  await page.getByRole('button', {name: 'Resolver', exact: true}).click();
  await expect(page.locator('#lab-results')).toContainText('(1, 2, 3)');
  await expect(page.locator('#lab-results')).toContainText('Sustitución de la solución en cada ecuación');
  await expect(page.locator('#alert')).toBeHidden();
});

test('Gauss-Seidel converge en ocho iteraciones sin depender de Plotly', async ({page}) => {
  await page.goto('/sistemas-lineales/gauss-seidel/');
  await page.getByRole('tab', {name: 'Calculadora', exact: true}).click();
  await page.getByRole('button', {name: 'Resolver', exact: true}).click();
  await expect(page.locator('#lab-results')).toContainText('8 iteraciones');
  await expect(page.locator('#lab-results')).toContainText('Convergió');
  await expect(page.locator('#lab-results')).toContainText('los resultados y tablas siguen disponibles');
});

test('el sistema singular no presenta una solución única', async ({page}) => {
  await page.goto('/sistemas-lineales/comparacion-metodos/');
  await page.locator('#example').selectOption('singular');
  await page.getByRole('button', {name: 'Resolver', exact: true}).click();
  await expect(page.locator('#lab-results')).toContainText('No hay solución única');
  await expect(page.locator('#lab-results')).toContainText('Sistema singular');
});

test('cambiar de ejemplo retira el resultado anterior y permite calcular el nuevo', async ({page}) => {
  await page.goto('/sistemas-lineales/eliminacion-gaussiana/');
  await page.getByRole('tab', {name: 'Calculadora', exact: true}).click();
  await page.getByRole('button', {name: 'Resolver', exact: true}).click();
  await expect(page.locator('#lab-results')).toContainText('(1, 2, 3)');
  await page.locator('#example').selectOption('dos');
  await expect(page.locator('#lab-results')).toContainText('Los datos cambiaron');
  await expect(page.locator('#lab-results')).not.toContainText('(1, 2, 3)');
  await page.getByRole('button', {name: 'Resolver', exact: true}).click();
  await expect(page.locator('#lab-results')).toContainText('(2, 3)');
});

test('una respuesta tardía no vuelve a mostrar datos anteriores a una edición', async ({page}) => {
  let captured, release, delivered;
  const requestCaptured = new Promise(resolve => {captured = resolve;});
  const gate = new Promise(resolve => {release = resolve;});
  const responseDelivered = new Promise(resolve => {delivered = resolve;});
  await page.route('**/api/linear/gauss/', async route => {
    const response = await route.fetch();
    captured();
    await gate;
    await route.fulfill({response}).catch(() => {});
    delivered();
  });
  await page.goto('/sistemas-lineales/eliminacion-gaussiana/');
  await page.getByRole('tab', {name: 'Calculadora', exact: true}).click();
  await page.getByRole('button', {name: 'Resolver', exact: true}).click();
  await requestCaptured;
  await page.locator('#b-0').fill('10');
  release();
  await responseDelivered;
  await expect(page.locator('#lab-results')).toContainText('Los datos cambiaron');
  await expect(page.locator('#lab-results')).not.toContainText('(1, 2, 3)');
  await expect(page.getByRole('button', {name: 'Resolver', exact: true})).toBeEnabled();
});

test('una entrada incompleta muestra el error sin conservar la solución anterior', async ({page}) => {
  await page.goto('/sistemas-lineales/eliminacion-gaussiana/');
  await page.getByRole('tab', {name: 'Calculadora', exact: true}).click();
  await page.getByRole('button', {name: 'Resolver', exact: true}).click();
  await expect(page.locator('#lab-results')).toContainText('(1, 2, 3)');
  await page.locator('#a-0-0').fill('');
  await page.getByRole('button', {name: 'Resolver', exact: true}).click();
  await expect(page.locator('#alert')).toContainText('Completa todos los campos');
  await expect(page.locator('#lab-results')).not.toContainText('(1, 2, 3)');
});

test('la comparación muestra el pivoteo y la divergencia al permutar las filas', async ({page}) => {
  await page.goto('/sistemas-lineales/comparacion-metodos/');
  await page.locator('#example').selectOption('permutado');
  await page.getByRole('button', {name: 'Resolver', exact: true}).click();
  await expect(page.locator('#lab-results')).toContainText('(1, 2, 3)');
  await expect(page.locator('#lab-results')).toContainText('Diverge');
  await page.getByText('Ver el procedimiento paso a paso de la eliminación gaussiana').click();
  await expect(page.locator('#lab-results')).toContainText('F1 ↔ F2');
});

test('las páginas y simuladores de ambos módulos cargan sin errores JavaScript', async ({page}) => {
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  for (const path of ['/', '/ecuaciones-no-lineales/', '/ecuaciones-no-lineales/errores/',
    '/ecuaciones-no-lineales/biseccion/', '/ecuaciones-no-lineales/comparar/',
    '/sistemas-lineales/', '/sistemas-lineales/formulacion/', '/buscar/?q=Gauss']) {
    const response = await page.goto(path);
    expect(response.status(), path).toBe(200);
  }
  expect(errors).toEqual([]);
});
