import {post,plot,line,points,format,showError,setMath,texNumber} from './common.js';
const $=id=>document.getElementById(id);
if($('concept-plot')){
  post('/api/nonlinear/graph/',{expression:'x^3 - x - 2',a:-2,b:2.5})
    .then(data=>plot($('concept-plot'),[line(data.x,data.y,'x³ − x − 2'),points([1.5213797068],[0],'Raíz ≈ 1.52138')]))
    .catch(error=>{$('concept-plot').textContent=error.message;});
}
const errorsForm=$('errors-form');
if(errorsForm){
  let version=0, controller=null, debounce;
  let sliderReference=null, sliderSpan=1, measurement=null;
  const validNumbers=()=>['true-value','approximate-value'].every(id=>$(id).value!==''&&Number.isFinite(Number($(id).value)));
  const validTolerance=()=>$('error-tolerance').value!==''&&Number.isFinite(Number($('error-tolerance').value))&&Number($('error-tolerance').value)>=0;
  function syncSlider(forceRange=false){
    const slider=$('approximation-slider'), output=$('approximation-live');
    if(!validNumbers()){
      slider.disabled=true;output.textContent='—';slider.setAttribute('aria-valuetext','Sin aproximación válida');return;
    }
    const a=Number($('true-value').value), b=Number($('approximate-value').value);
    const tolerance=validTolerance()?Number($('error-tolerance').value):0;
    if(forceRange||sliderReference!==a||Math.abs(b-a)>sliderSpan||tolerance*2>sliderSpan){
      sliderReference=a;
      sliderSpan=Math.max(Math.abs(b-a)*1.15,Math.abs(a)*.2,tolerance*2,1);
    }
    const usable=Number.isFinite(sliderSpan)&&Number.isFinite(a-sliderSpan)&&Number.isFinite(a+sliderSpan);
    slider.disabled=!usable;
    slider.value=usable?String(Math.round(500+500*(b-a)/sliderSpan)):'500';
    output.textContent=format(b);
    slider.setAttribute('aria-valuetext',usable?`Aproximación ${format(b)}`:'Rango no disponible');
  }
  function toleranceInterval(){
    if(!validNumbers()||!validTolerance())return null;
    const a=Number($('true-value').value), tolerance=Number($('error-tolerance').value);
    const lower=a-tolerance, upper=a+tolerance;
    return Number.isFinite(lower)&&Number.isFinite(upper)?[lower,upper]:null;
  }
  function presentation(){
    const digits=Number($('display-decimals').value), value=Number($('approximate-value').value);
    $('decimal-count').textContent=digits;
    $('display-preview').textContent=$('approximate-value').value!==''&&Number.isFinite(value)
      ?`Aproximación mostrada: ${value.toFixed(digits)}. El valor interno no cambia.`:'Introduce una aproximación finita.';
    const tolerance=Number($('error-tolerance').value);
    const matching=measurement&&measurement.reference===Number($('true-value').value)&&measurement.approximation===value&&measurement.tolerance===tolerance;
    const error=matching?measurement.absolute:0;
    const valid=validNumbers()&&validTolerance()&&matching;
    const accepted=valid&&measurement.accepted;
    $('tolerance-feedback').textContent=valid
      ?`${accepted?'Cumple':'No cumple'}: error absoluto ${format(error)} ${accepted?'≤':'>'} tolerancia ${format(tolerance)}.`
      :validNumbers()&&validTolerance()?'Comprobando la tolerancia…':'Introduce valores finitos y una tolerancia no negativa.';
    $('tolerance-feedback').dataset.outcome=valid?(accepted?'accepted':'rejected'):'pending';
    $('try-boundary').disabled=!valid;
    $('challenge-feedback').textContent=valid
      ?accepted?`Meta alcanzada: ${format(error)} ≤ ${format(tolerance)}. Prueba alejar la aproximación y observa cuándo deja de cumplir.`
        :`Aún faltan ${format(error-tolerance)} unidades para entrar en el límite. Acerca la aproximación a la referencia.`
      :'Introduce valores finitos y una tolerancia no negativa para comenzar.';
    $('tolerance-interval').textContent=toleranceInterval()?.map(format).join(' a ')||'No disponible';
  }
  function invalidate(){
    version++;controller?.abort();clearTimeout(debounce);showError('');
    for(const key of ['absolute','relative','percentage'])$(key).textContent='—';
    $('error-state').textContent='Datos modificados';$('error-message').textContent='';
    setMath($('error-worked'),null,'Completa los datos para ver el desarrollo.');
    if(window.Plotly&&$('error-plot').data)window.Plotly.purge($('error-plot'));
    $('error-plot').textContent='Esperando datos válidos.';
  }
  async function calculate(){
    invalidate();syncSlider();presentation();
    if(!validNumbers()||!errorsForm.reportValidity())return;
    const seq=version;controller=new AbortController();$('error-state').textContent='Calculando…';
    try{
      const values=Object.fromEntries(new FormData(errorsForm));
      if(validTolerance())values.tolerance=$('error-tolerance').value;
      const data=await post('/api/nonlinear/errors/',values,controller.signal);
      if(seq!==version)return;
      measurement={...data,reference:Number(values.true_value),approximation:Number(values.approximate_value),tolerance:Number(values.tolerance)};
      presentation();
      ['absolute','relative','percentage'].forEach(key=>$(key).textContent=data[key]===null?'No definido':format(data[key])+(key==='percentage'?' %':''));
      $('error-message').textContent=data.message;$('error-state').textContent='Actualizado';
      const a=Number(values.true_value),b=Number(values.approximate_value);
      const v=texNumber(a), approx=texNumber(b), absolute=texNumber(data.absolute);
      const relative=data.relative===null?'E_r, E_p: no definidos':`Er = ${format(data.relative)}; Ep = ${format(data.percentage)} %`;
      const second=data.relative===null
        ?(a===0?String.raw`E_r&=\frac{E_a}{0}\quad\text{no definido}`:String.raw`E_r,E_p&:\ \text{fuera del rango numérico}`)
        :String.raw`E_r&=\frac{${absolute}}{|${v}|}\approx ${texNumber(data.relative)}\\ E_p&=100E_r\approx ${texNumber(data.percentage)}\%`;
      setMath($('error-worked'),String.raw`\begin{aligned}E_a&=|${v}-(${approx})|\approx ${absolute}\\ ${second}\end{aligned}`,
        `Ea = |${format(a)} − (${format(b)})| ≈ ${format(data.absolute)}; ${relative}.`);
      await renderErrorPlot(a,b);
    }catch(error){if(seq!==version||error.name==='AbortError')return;showError(error.message);$('error-state').textContent='Revisa los datos';}
  }
  async function renderErrorPlot(a,b){
    const interval=toleranceInterval();
    const spread=Math.max(Math.abs(a-b),interval?Math.abs(interval[1]-interval[0]):0,1);
    const padding=spread*.08;
    const lower=Math.min(a,b,interval?.[0]??a)-padding, upper=Math.max(a,b,interval?.[1]??a)+padding;
    const axis=Number.isFinite(lower)&&Number.isFinite(upper)?{range:[lower,upper]}:{};
    await plot($('error-plot'),[
      line([a,b],[0,0],'Distancia',{line:{width:4,color:'#8a7acb'},hoverinfo:'skip'}),
      points([a],[0],'Referencia',{marker:{size:12,color:'#986327'},hovertemplate:'Referencia: %{x:.9g}<extra></extra>'}),
      points([b],[0],'Aproximación',{marker:{size:12,color:'#496f96'},hovertemplate:'Aproximación: %{x:.9g}<extra></extra>'}),
    ],{xaxis:{...axis,title:'Valor en la recta'},yaxis:{visible:false,range:[-1,1]},
      shapes:interval?[{type:'rect',xref:'x',yref:'paper',x0:interval[0],x1:interval[1],y0:0,y1:1,
        fillcolor:'rgba(87,70,187,0.12)',line:{color:'#5746bb',width:1},layer:'below'}]:[]});
  }
  $('display-decimals').addEventListener('input',presentation);
  $('error-tolerance').addEventListener('input',calculate);
  errorsForm.addEventListener('input',()=>{invalidate();syncSlider();presentation();debounce=setTimeout(calculate,300);});
  errorsForm.addEventListener('submit',event=>{event.preventDefault();calculate();});
  $('approximation-slider').addEventListener('input',()=>{
    const a=Number($('true-value').value), slider=Number($('approximation-slider').value);
    $('approximate-value').value=String(Number((a+(slider-500)*sliderSpan/500).toPrecision(12)));
    $('approximate-value').dispatchEvent(new Event('input',{bubbles:true}));
  });
  $('try-boundary').addEventListener('click',()=>{
    if(!validNumbers()||!validTolerance())return;
    const a=Number($('true-value').value), b=Number($('approximate-value').value), tolerance=Number($('error-tolerance').value);
    const next=Math.sign(b-a||1)>0?measurement.boundary_upper:measurement.boundary_lower;
    if(!Number.isFinite(next))return;
    $('approximate-value').value=String(next);calculate();
  });
  $('error-example').addEventListener('change',()=>{
    const examples={positive:[10,9.8],negative:[-5,-4.9],zero:[0,.001]};
    const [reference,approximation]=examples[$('error-example').value];
    $('true-value').value=reference;$('approximate-value').value=approximation;calculate();
  });
  calculate();
}
