// Los valores que muestran las animaciones coinciden con los ejercicios resueltos del catálogo.
const {test} = require('node:test');
const assert = require('node:assert/strict');
const {pathToFileURL} = require('node:url');
const {resolve} = require('node:path');

const load = name => import(pathToFileURL(resolve(__dirname, '../static/js/animations', name)).href);
const six = value => value.toFixed(6);

test('bisección, Newton y escenas de raíces reproducen las tablas a seis decimales', async () => {
  const {bisectionIterations, newtonIterations, f, rootScenes} = await load('root-scenes.js');
  const bisection = bisectionIterations(f, 1, 2, 4);
  assert.deepEqual(bisection.map(it => six(it.c)), ['1.500000', '1.750000', '1.625000', '1.562500']);
  assert.deepEqual(bisection.map(it => six(it.fc)), ['-0.125000', '1.609375', '0.666016', '0.252197']);
  const newton = newtonIterations(1.5, 3);
  assert.deepEqual(newton.map(it => six(it.next)), ['1.521739', '1.521380', '1.521380']);
  for (const [key, factory] of Object.entries(rootScenes)) {
    const scene = factory();
    assert.ok(scene.frames.length >= 4, key);
    for (const frame of scene.frames) {
      assert.equal(typeof frame.title, 'string', key);
      assert.equal(typeof frame.draw, 'function', key);
    }
  }
  const secant = rootScenes.secant().frames.map(frame => frame.title);
  assert.match(secant[2], /1\.531169/);
  const fixed = rootScenes['fixed-point']().frames.map(frame => frame.text).join(' ');
  for (const value of ['1.518294', '1.520935', '1.521316', '1.521370']) assert.ok(fixed.includes(value), value);
  const multiple = rootScenes['multiple-roots']().frames.map(frame => frame.text).join(' ');
  for (const value of ['0.934959', '0.999264', '1.000000', '1.438095', '1.232168', '1.120108']) assert.ok(multiple.includes(value), value);
});

test('eliminación gaussiana y Gauss-Seidel llegan a x = (1, 2, 3)', async () => {
  const {gaussFrames, seidelHistory, BASE_A, BASE_B} = await load('linear-scenes.js');
  const gauss = gaussFrames(BASE_A, BASE_B);
  assert.match(gauss.at(-1).text, /x = \(1, 2, 3\)/);
  assert.ok(gauss.some(frame => frame.text.includes('0.157895')));
  const history = seidelHistory(BASE_A, BASE_B);
  assert.equal(history.length - 1, 8);
  assert.deepEqual(history[1].x.map(six), ['2.250000', '2.350000', '2.733333']);
  assert.deepEqual(history[2].x.map(six), ['0.979167', '2.057500', '2.993889']);
  assert.deepEqual(history.at(-1).x.map(six), ['1.000000', '2.000000', '3.000000']);
});
