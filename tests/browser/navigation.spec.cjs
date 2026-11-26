const {test, expect, devices} = require('@playwright/test');

test.use({...devices['iPhone 13'], defaultBrowserType: 'chromium'});

test('el menú táctil funciona mientras los módulos y las fórmulas siguen cargando', async ({page}) => {
  await page.route(/^https:\/\//, route => route.abort());
  await page.route('**/static/js/app.js*', () => {});
  await page.route('**/static/vendor/mathjax/**', () => {});
  await page.goto('/', {waitUntil: 'commit'});
  await page.locator('#menu-toggle').tap();
  await expect(page.locator('#sidebar')).toHaveClass(/open/);
  await page.locator('.primary-learning').getByRole('link', {name: 'Mi avance', exact: true}).tap();
  await page.waitForURL('**/avance/', {waitUntil: 'commit'});
  await page.locator('#menu-toggle').tap();
  await expect(page.locator('#sidebar')).toHaveClass(/open/);
  await page.locator('#menu-close').tap();
  await expect(page.locator('#sidebar')).not.toHaveClass(/open/);
  await expect(page.locator('#menu-toggle')).toBeFocused();
});
