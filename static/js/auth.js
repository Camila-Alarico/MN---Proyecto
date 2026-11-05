// Progressive enhancement: authentication and validation remain Django's responsibility.
for (const button of document.querySelectorAll('[data-password-target]')) {
  const input = document.getElementById(button.dataset.passwordTarget);
  if (!input) continue;
  const label = document.querySelector(`label[for="${input.id}"]`).textContent.replace(/:$/, '').toLocaleLowerCase('es');
  button.hidden = false;
  button.addEventListener('click', () => {
    const visible = input.type === 'password';
    input.type = visible ? 'text' : 'password';
    button.textContent = visible ? 'Ocultar' : 'Mostrar';
    button.setAttribute('aria-label', `${visible ? 'Ocultar' : 'Mostrar'} ${label}`);
    button.setAttribute('aria-pressed', String(visible));
  });
}
