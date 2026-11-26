// Centímetros en centésimas enteras: comparar el límite sin ruido binario.
document.querySelectorAll('[data-measurement-demo]').forEach(root => {
  const find = name => root.querySelector(`[data-measure-${name}]`);
  const slider = find('slider');
  const render = () => {
    const hundredths = Number(slider.value), value = (hundredths / 100).toFixed(2);
    const distance = Math.abs(1000 - hundredths), error = (distance / 100).toFixed(2);
    const accepted = distance <= 10;
    find('value').textContent = value;
    find('inline').textContent = `${value} cm`;
    find('equation').textContent = value;
    find('error').textContent = `${error} cm`;
    find('pointer').style.left = `${hundredths - 950}%`;
    slider.setAttribute('aria-valuetext', `${value} centímetros`);
    find('verdict').dataset.accepted = String(accepted);
    find('decision').textContent = accepted ? 'Cumple la tolerancia' : 'No cumple la tolerancia';
    find('reason').textContent = distance === 10
      ? 'Está justo en el límite: 0.10 cm ≤ 0.10 cm. La igualdad también cumple.'
      : `El error es ${error} cm ${accepted ? '≤' : '>'} 0.10 cm, el máximo permitido.`;
  };
  slider.addEventListener('input', render);
  find('boundary').addEventListener('click', () => { slider.value = '1010'; render(); });
  find('reset').addEventListener('click', () => { slider.value = '980'; render(); });
  render();
});
