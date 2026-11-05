// Animaciones de los ejemplos de teoría (cargado por app.js solo si la página tiene alguna).
import {TheoryAnimation} from './animations/engine.js';
import {scenes} from './animations/scenes.js';

document.querySelectorAll('[data-theory-animation]').forEach(root => {
  const factory = scenes[root.dataset.scene];
  if (factory) root.theoryAnimation = new TheoryAnimation(root, factory);
});
