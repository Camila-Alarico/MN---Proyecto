// Registro de escenas: la clave coincide con `data-scene` en components/theory_animation.html.
import {rootScenes} from './root-scenes.js';
import {errorScenes} from './error-scenes.js';
import {linearScenes} from './linear-scenes.js';

export const scenes = {...rootScenes, ...errorScenes, ...linearScenes};
