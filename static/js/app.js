import './method-sections.js';
import {post} from './nonlinear/common.js';
const toggle=document.getElementById('menu-toggle'),sidebar=document.getElementById('sidebar'),shade=document.getElementById('sidebar-shade');
const workspace=document.querySelector('.workspace');
const mobile=matchMedia('(max-width:1100px)');
const root=document.documentElement;
const hotzone=document.getElementById('sidebar-hotzone'),pin=document.getElementById('sidebar-pin');
const PIN_KEY='numlearn:sidebar-pinned';
const isPinned=()=>root.classList.contains('sidebar-pinned');
function setMenu(open){workspace.inert=mobile.matches&&open;sidebar.inert=mobile.matches&&!open;sidebar.classList.toggle('open',open);toggle.setAttribute('aria-expanded',String(open));toggle.setAttribute('aria-label',open?'Cerrar menú':'Abrir menú');shade.hidden=!open;if(open)sidebar.querySelector('a').focus();else toggle.focus();}
function syncMenu(){const open=mobile.matches&&sidebar.classList.contains('open');workspace.inert=open;sidebar.inert=mobile.matches&&!open;shade.hidden=!open;toggle.setAttribute('aria-expanded',String(open));if(!mobile.matches)sidebar.classList.remove('open');}
mobile.addEventListener('change',()=>{syncMenu();peek(false,true);if(mobile.matches)toggle.setAttribute('aria-label',sidebar.classList.contains('open')?'Cerrar menú':'Abrir menú');});syncMenu();
toggle.addEventListener('click',()=>{
  if(!mobile.matches){const show=!sidebar.classList.contains('is-peeking');peek(show,true);if(show)sidebar.querySelector('a').focus();return;}
  setMenu(!sidebar.classList.contains('open'));
});
shade.addEventListener('click',()=>setMenu(false));
document.getElementById('menu-close')?.addEventListener('click',()=>setMenu(false));
document.addEventListener('keydown',event=>{
  if(event.key!=='Escape')return;
  if(sidebar.classList.contains('open'))setMenu(false);
  else if(sidebar.classList.contains('is-peeking')){peek(false,true);if(sidebar.contains(document.activeElement))toggle.focus();}
});
document.querySelectorAll('.complete-topic').forEach(button=>button.addEventListener('click',async()=>{button.disabled=true;try{await post(button.dataset.endpoint||'/api/nonlinear/progress/',{topic:button.dataset.topic});location.reload();}catch(error){button.textContent=error.message;button.disabled=false;}}));

document.addEventListener('keydown',event=>{
  if(event.key!=='Tab'||!mobile.matches||!sidebar.classList.contains('open'))return;
  const items=[...sidebar.querySelectorAll('a,button,summary')].filter(item=>item.getClientRects().length);
  const first=items[0],last=items[items.length-1];
  if(event.shiftKey&&document.activeElement===first){event.preventDefault();last.focus();}
  else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first.focus();}
});

sidebar.querySelectorAll('a').forEach(link=>link.addEventListener('click',()=>{
  if(mobile.matches&&sidebar.classList.contains('open'))setMenu(false);
}));

// Menú lateral de escritorio: oculto por defecto, aparece al acercar el puntero al borde
// izquierdo y se puede fijar con el botón del dardo (preferencia guardada en localStorage).
let hideTimer;
function peek(show,immediate=false){
  clearTimeout(hideTimer);
  if(show){if(!isPinned()&&!mobile.matches)sidebar.classList.add('is-peeking');syncToggle();return;}
  const hide=()=>{
    if(!immediate&&(sidebar.matches(':hover')||hotzone?.matches(':hover')))return;
    sidebar.classList.remove('is-peeking');syncToggle();
  };
  if(immediate)hide();else hideTimer=setTimeout(hide,260);
}
function syncToggle(){
  if(mobile.matches)return;
  const shown=isPinned()||sidebar.classList.contains('is-peeking');
  toggle.setAttribute('aria-expanded',String(shown));
  toggle.setAttribute('aria-label',shown?'Ocultar menú':'Mostrar menú');
}
function setPinned(value,{animate=false,persist=true}={}){
  root.classList.toggle('sidebar-pinned',value);
  if(persist){try{localStorage.setItem(PIN_KEY,value?'1':'0');}catch{}}
  if(pin){
    pin.setAttribute('aria-pressed',String(value));
    const label=value?'Desfijar menú lateral':'Fijar menú lateral';
    pin.setAttribute('aria-label',label);pin.title=value?'Desfijar menú':'Fijar menú';
    if(animate&&value){pin.classList.remove('is-thrown');void pin.offsetWidth;pin.classList.add('is-thrown');}
  }
  if(value)sidebar.classList.remove('is-peeking');
  else if(persist)sidebar.classList.add('is-peeking'); // sigue visible mientras el puntero esté encima
  syncToggle();
  if(persist)setTimeout(()=>window.dispatchEvent(new Event('resize')),320); // las gráficas se adaptan al nuevo ancho
}
if(pin){
  setPinned(isPinned(),{persist:false});
  pin.addEventListener('click',()=>setPinned(!isPinned(),{animate:true}));
  pin.addEventListener('animationend',()=>pin.classList.remove('is-thrown'));
}
syncToggle();
hotzone?.addEventListener('mouseenter',()=>peek(true));
hotzone?.addEventListener('mouseleave',()=>peek(false));
hotzone?.addEventListener('click',()=>peek(true));
sidebar.addEventListener('mouseenter',()=>{if(!isPinned())peek(true);});
sidebar.addEventListener('mouseleave',()=>{if(!isPinned())peek(false);});
sidebar.addEventListener('focusout',event=>{if(!isPinned()&&!sidebar.contains(event.relatedTarget))peek(false);});
document.addEventListener('pointerdown',event=>{
  if(isPinned()||mobile.matches||!sidebar.classList.contains('is-peeking'))return;
  if(!sidebar.contains(event.target)&&!toggle.contains(event.target)&&event.target!==hotzone&&!hotzone?.contains(event.target))peek(false,true);
});
requestAnimationFrame(()=>requestAnimationFrame(()=>root.classList.add('sidebar-ready')));

function revealProgram(){if(location.hash==='#modules'){const program=document.getElementById('modules');if(program?.tagName==='DETAILS')program.open=true;}}
window.addEventListener('hashchange',revealProgram);revealProgram();

// Animaciones de los ejemplos de teoría: solo se cargan si la página las contiene.
if(document.querySelector('[data-theory-animation]'))import('./theory-animation.js');
