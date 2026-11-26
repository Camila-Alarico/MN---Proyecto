import './method-sections.js';
import {post} from './nonlinear/common.js';
document.querySelectorAll('.complete-topic').forEach(button=>button.addEventListener('click',async()=>{button.disabled=true;try{await post(button.dataset.endpoint||'/api/nonlinear/progress/',{topic:button.dataset.topic});location.reload();}catch(error){button.textContent=error.message;button.disabled=false;}}));

function revealProgram(){if(location.hash==='#modules'){const program=document.getElementById('modules');if(program?.tagName==='DETAILS')program.open=true;}}
window.addEventListener('hashchange',revealProgram);revealProgram();

// Animaciones de los ejemplos de teoría: solo se cargan si la página las contiene.
if(document.querySelector('[data-theory-animation]'))import('./theory-animation.js');
