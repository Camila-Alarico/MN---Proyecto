import {line,points} from './common.js';
export function visualize(method,result,index){
  const traces=[line(result.plot.x,result.plot.y,method==='fixed-point'?'g(x)':'f(x)')];
  const row=result.iterations[index]; const shapes=[];
  if(method==='fixed-point') traces.push(line(result.plot.x,result.plot.x,'y = x',{line:{color:'#a7afc2',dash:'dash'}}));
  if(!row){if(result.converged && result.root!=null)traces.push(points([result.root],[method==='fixed-point'?result.root:0],'Aproximación'));return{traces,shapes};}
  if(['bisection','false-position'].includes(method)){
    traces.push(points([row.a,row.b],[row.fa,row.fb],'Extremos a, b'),points([row.x],[row.fx],method==='bisection'?'Xm':'xr'));
    shapes.push({type:'rect',xref:'x',yref:'paper',x0:row.a,x1:row.b,y0:0,y1:1,fillcolor:'#5746bb',opacity:.09,line:{width:0},layer:'below'});
    if(method==='false-position')traces.push(line([row.a,row.b],[row.fa,row.fb],'Recta secante',{line:{dash:'dash',color:'#92622a'}}));
  }else if(method==='newton'){
    traces.push(points([row.xn],[row.fxn],'Punto de tangencia'),line([row.xn,row.x],[row.fxn,0],'Tangente',{line:{color:'#92622a',dash:'dash'}}));
  }else if(method==='secant'){
    const slope=(row.fxn-row.fprevious)/(row.xn-row.previous);
    const xs=[row.previous,row.xn,row.x].sort((a,b)=>a-b);
    traces.push(points([row.previous,row.xn],[row.fprevious,row.fxn],'Puntos de la secante'),line(xs,xs.map(x=>row.fxn+slope*(x-row.xn)),'Recta secante',{line:{dash:'dash',color:'#92622a'}}));
  }else if(method==='fixed-point'){
    const xs=[],ys=[];result.iterations.slice(0,index+1).forEach((r,i)=>{xs.push(r.xn,r.xn,r.x);ys.push(i===0?0:r.xn,r.x,r.x);});
    traces.push(line(xs,ys,'Escalera de iteraciones',{line:{color:'#536b8b'}}));
  }else{traces.push(points([row.xn],[row.fxn],'Aproximación anterior'));}
  traces.push(points([row.x],[method==='fixed-point'?row.x:0],'Nueva aproximación',{marker:{color:'#5746bb',size:11,symbol:'diamond'}}));
  return{traces,shapes};
}
export const columns={
  bisection:[['n','n'],['a','a'],['b','b'],['x','Xm'],['fa','f(a)'],['fb','f(b)'],['fx','f(Xm)'],['error_bound','Cota de error'],['error','Paso |Δx|'],['new_a','Nuevo a'],['new_b','Nuevo b']],
  'false-position':[['n','n'],['a','a'],['b','b'],['x','xr'],['fa','f(a)'],['fb','f(b)'],['fx','f(xr)'],['error','Paso |Δx|'],['new_a','Nuevo a'],['new_b','Nuevo b']],
  newton:[['n','n'],['xn','xn'],['fxn','f(xn)'],['dfx','f′(xn)'],['x','x(n+1)'],['fx','f(x(n+1))'],['error','Paso |Δx|']],
  'fixed-point':[['n','n'],['xn','xn'],['x','g(xn)'],['error','Paso |Δx|']],
  secant:[['n','n'],['previous','x(n−1)'],['xn','xn'],['fxn','f(xn)'],['x','x(n+1)'],['fx','f(x(n+1))'],['error','Paso |Δx|']],
  'multiple-roots':[['n','n'],['xn','xn'],['fxn','f(xn)'],['dfx','f′(xn)'],['ddfx','f″(xn)'],['x','x(n+1)'],['fx','f(x(n+1))'],['error','Paso |Δx|']]
};
