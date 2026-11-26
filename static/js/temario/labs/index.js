// Registro de laboratorios: la clave coincide con `lab.kind` de cada lección (temario/lessons/).
import {mountLab} from './framework.js';
import {precision, taylor} from './unit1.js';
import {polyroots} from './unit2.js';
import {gaussjordan, iterative, lu} from './unit3.js';
import {fourier, newtoninterp, regression, splines} from './unit4.js';
import {differentiation, integration} from './unit5.js';
import {odeEuler, odeRk, pde} from './unit6.js';

export const LABS = {precision, taylor, polyroots, gaussjordan, lu, iterative, regression, newtoninterp, splines, fourier,
                     integration, differentiation, 'ode-euler': odeEuler, 'ode-rk': odeRk, pde};

export function mount(container) {
  const definition = LABS[container.dataset.lab];
  if (!definition) { container.textContent = 'Este laboratorio no está disponible.'; return null; }
  return mountLab(container, definition);
}
