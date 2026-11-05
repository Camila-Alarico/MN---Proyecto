import {chartLayout} from './chart-theme.js';
// URL canónica de cada método, publicada una sola vez en base.html (ver core/context_processors.py).
export const simulatorUrls = JSON.parse(document.getElementById('simulator-urls')?.textContent || '{}');
export const format = value => value == null ? '—' : typeof value === 'number' ? Number(value.toPrecision(9)).toString() : String(value);
export async function post(endpoint, payload, signal) {
  const response = await fetch(endpoint, {method:'POST', credentials:'same-origin', signal,
    headers:{'Content-Type':'application/json','X-CSRFToken':document.querySelector('[name=csrfmiddlewaretoken]').value}, body:JSON.stringify(payload)});
  let result;
  try { result = await response.json(); } catch { throw new Error('El servidor no pudo responder. Recarga la página y vuelve a intentar.'); }
  if (!response.ok || !result.success) throw new Error(result.error || 'No se pudo completar la solicitud.');
  return result;
}
export function showError(message) {
  const target = document.getElementById('alert');
  if (target) {target.textContent = message; target.hidden = !message;}
}
export function table(target, columns, rows, active=-1, onSelect=null) {
  const element = document.createElement('table'); element.className = 'table';
  element.createCaption().textContent = onSelect ? 'Selecciona un paso para ver su construcción en la gráfica.' : 'Resultados numéricos';
  const head = element.createTHead().insertRow();
  columns.forEach(([,label]) => {const th=document.createElement('th'); th.scope='col'; th.textContent=label; head.append(th);});
  const body=element.createTBody();
  rows.forEach((row,index) => {const tr=body.insertRow(); if(index===active)tr.className='active-row';
    columns.forEach(([key],column) => {const cell=tr.insertCell(); if(column===0 && onSelect){const button=document.createElement('button');button.type='button';button.className='iteration-button';button.textContent=format(row[key]);button.setAttribute('aria-label',`Ver iteración ${row.n}`);button.setAttribute('aria-pressed',String(index===active));button.addEventListener('click',()=>onSelect(index));cell.append(button);}else cell.textContent=format(row[key]);});});
  target.replaceChildren(element);
}
export async function plot(target, traces, extra={}) {
  if (!window.Plotly) {target.textContent='No se pudo cargar Plotly. Comprueba tu conexión a Internet; los resultados y tablas siguen disponibles.'; return;}
  if (!target.data) target.replaceChildren();
  await Plotly.react(target,traces,chartLayout(extra),
    {responsive:true,displaylogo:false,modeBarButtonsToRemove:['lasso2d','select2d']});
}
export const line=(x,y,name,extras={})=>({x,y,name,type:'scatter',mode:'lines',connectgaps:false,line:{width:2},...extras});
export const points=(x,y,name,extras={})=>({x,y,name,type:'scatter',mode:'markers',marker:{size:9},...extras});
export function busy(button,value,label='Calculando…') {
  if(value){button.dataset.label=button.textContent;button.textContent=label;button.classList.add('loading');}
  else{button.textContent=button.dataset.label||button.textContent;button.classList.remove('loading');}
  button.disabled=value;
}
export async function typeset(target) {if(window.MathJax?.typesetPromise) await MathJax.typesetPromise([target]);}


// Serialize dynamic MathJax work and discard outdated replacements.
let mathQueue = Promise.resolve();
const mathVersions = new WeakMap();
let mathReady;
async function mathEngine() {
  if (!window.MathJax?.typesetPromise) {
    if (!mathReady) mathReady = new Promise(resolve => {
      const loader = document.getElementById('mathjax-loader');
      if (!loader || document.readyState === 'complete') {resolve(); return;}
      const done = () => {
        loader.removeEventListener('load', done);
        loader.removeEventListener('error', done);
        window.removeEventListener('load', done);
        resolve();
      };
      loader.addEventListener('load', done, {once: true});
      loader.addEventListener('error', done, {once: true});
      window.addEventListener('load', done, {once: true});
    });
    await mathReady;
  }
  const math = window.MathJax;
  if (math?.startup?.promise) await math.startup.promise;
  return math;
}
export function setMath(target, tex, fallback, {inline = false} = {}) {
  const version = (mathVersions.get(target) || 0) + 1;
  mathVersions.set(target, version);
  window.MathJax?.typesetClear?.([target]);
  target.textContent = fallback;
  const task = async () => {
    if (mathVersions.get(target) !== version) return;
    try {
      const math = await mathEngine();
      if (mathVersions.get(target) !== version || target.isConnected === false) return;
      math?.typesetClear?.([target]);
      target.textContent = fallback;
      if (tex && math?.typesetPromise) {
        target.textContent = inline ? String.raw`\(${tex}\)` : String.raw`\[${tex}\]`;
        await math.typesetPromise([target]);
      }
    }
    catch { if (mathVersions.get(target) === version) target.textContent = fallback; }
  };
  mathQueue = mathQueue.then(task, task);
  return mathQueue;
}
export function texNumber(value) {
  return format(value).replace(/e([+-]?\d+)/i, (_, power) => String.raw`\times 10^{${Number(power)}}`);
}
