const {test} = require('node:test');
const assert = require('node:assert/strict');

test('LaTeX dinámico usa delimitadores válidos, conserva el dato reciente y mantiene alternativas', async t => {
  global.document = {getElementById: () => null, readyState: 'complete'};
  global.window = {};
  try {
    const {setMath, texNumber} = await import('../static/js/nonlinear/common.js');
    await t.test('científica y delimitadores de presentación e inline', async () => {
      const seen = [];
      window.MathJax = {startup: {promise: Promise.resolve()}, typesetClear() {}, async typesetPromise([target]) {seen.push(target.textContent);}};
      await setMath({textContent: ''}, String.raw`E_r=\frac{0.5}{20}`, 'Er = 0.5 / 20');
      await setMath({textContent: ''}, 'E_a=0.5', 'Ea = 0.5', {inline: true});
      assert.equal(seen[0], String.raw`\[E_r=\frac{0.5}{20}\]`);
      assert.equal(seen[1], String.raw`\(E_a=0.5\)`);
      assert.equal(texNumber(1e-8), String.raw`1\times 10^{-8}`);
    });
    await t.test('una actualización durante la carga no restaura la fórmula vieja', async () => {
      let release;
      const gate = new Promise(resolve => {release = resolve;});
      const seen = [];
      window.MathJax = {startup: {promise: gate}, typesetClear() {}, async typesetPromise([target]) {seen.push(target.textContent);}};
      const target = {textContent: ''};
      const old = setMath(target, 'E_a=1', 'Ea = 1');
      await new Promise(setImmediate);
      const latest = setMath(target, 'E_a=0.5', 'Ea = 0.5');
      release(); await Promise.all([old, latest]);
      assert.deepEqual(seen, [String.raw`\[E_a=0.5\]`]);
    });
    await t.test('sin motor de fórmulas conserva texto matemático legible', async () => {
      delete window.MathJax;
      const target = {textContent: ''};
      await setMath(target, String.raw`\frac{1}{2}`, '1 / 2');
      assert.equal(target.textContent, '1 / 2');
    });
    await t.test('un error de carga no deja LaTeX crudo', async () => {
      window.MathJax = {startup: {promise: Promise.reject(new Error('load failed'))}};
      const target = {textContent: ''};
      await setMath(target, 'E_a=0.5', 'Ea = 0.5');
      assert.equal(target.textContent, 'Ea = 0.5');
    });
  } finally {delete global.window; delete global.document;}
});
