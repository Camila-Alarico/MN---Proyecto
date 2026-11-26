const {test,expect}=require('@playwright/test');
const AxeBuilder=require('@axe-core/playwright').default;
test.beforeEach(async({page})=>{await page.route(/^https:\/\//,r=>r.abort());});

test('errores usa el formato común y conserva el ejemplo y ambas animaciones',async({page},info)=>{
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('/ecuaciones-no-lineales/errores/');
  await expect(page.getByRole('heading',{name:'Errores numéricos',exact:true}).first()).toBeVisible();
  await expect(page.getByRole('tab')).toHaveText(['Teoría','Ejercicio resuelto','Laboratorio','Comprueba']);
  await expect(page.locator('#tipos')).toBeVisible();
  await expect(page.locator('#error-plot')).toBeHidden();
  await page.screenshot({path:info.outputPath('errores-teoria.png'),fullPage:true});
  await page.getByRole('tab',{name:'Ejercicio resuelto',exact:true}).click();
  await expect(page.locator('[data-measurement-demo]')).toBeVisible();
  await page.getByRole('button',{name:'Probar el límite',exact:true}).click();
  await expect(page.locator('[data-measure-verdict]')).toHaveAttribute('data-accepted','true');
  const animation=page.getByTestId('theory-animation-errors');
  await animation.getByRole('button',{name:'Iniciar animación'}).click();
  await animation.getByTestId('anim-next').click();
  await expect(animation.getByTestId('anim-counter')).toContainText('Paso 2');
  await animation.getByRole('button',{name:'Cerrar animación'}).click();
  await page.locator('#practicar > summary').click();
  const derivative=page.getByTestId('theory-animation-derivative-perturbation');
  await derivative.getByRole('button',{name:'Iniciar animación'}).click();
  await derivative.getByTestId('anim-next').click();
  await expect(derivative.getByTestId('anim-counter')).toContainText('Paso 2');
  expect(errors).toEqual([]);
});

test('los marcadores antiguos abren la pestaña correcta y las preguntas explican la respuesta',async({page})=>{
  await page.goto('/ecuaciones-no-lineales/errores/#practicar');
  await expect(page.getByRole('tab',{name:'Ejercicio resuelto',exact:true})).toHaveAttribute('aria-selected','true');
  await expect(page.locator('#practicar')).toBeVisible();
  await page.goto('/ecuaciones-no-lineales/errores/#tipos');
  await expect(page.getByRole('tab',{name:'Teoría',exact:true})).toHaveAttribute('aria-selected','true');
  await page.getByRole('tab',{name:'Comprueba',exact:true}).click();
  const cards=page.locator('.check-card');
  await cards.nth(0).getByRole('button',{name:'0.20 cm',exact:true}).click();
  await cards.nth(1).getByRole('button',{name:'Sí, porque el límite incluye la igualdad',exact:true}).click();
  await expect(page.locator('#check-score')).toContainText('2 de 2');
  await expect(cards.nth(0).locator('.check-feedback')).toContainText('Es una distancia');
});

test('las cuatro pestañas conservan accesibilidad y caben en móvil',async({page},info)=>{
  await page.goto('/ecuaciones-no-lineales/errores/');
  for(const name of ['Teoría','Ejercicio resuelto','Laboratorio','Comprueba']){
    await page.getByRole('tab',{name,exact:true}).click();
    const result=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa']).analyze();
    expect(result.violations.map(v=>v.id)).toEqual([]);
  }
  await page.setViewportSize({width:390,height:844});
  for(const name of ['Teoría','Ejercicio resuelto','Laboratorio','Comprueba']){
    await page.getByRole('tab',{name,exact:true}).click();
    await expect.poll(()=>page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth), {message:`Desbordamiento horizontal en ${name}`}).toBe(true);
  }
  await page.getByRole('tab',{name:'Teoría',exact:true}).click();
  await page.evaluate(()=>scrollTo(0,0));
  await page.screenshot({path:info.outputPath('errores-movil.png'),fullPage:true});
});
