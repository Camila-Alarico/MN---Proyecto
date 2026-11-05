// Utilidades de formato compartidas por las escenas.
const SUB = '₀₁₂₃₄₅₆₇₈₉';
const SUP = '⁰¹²³⁴⁵⁶⁷⁸⁹';
export const sup = n => String(n).split('').map(d => SUP[Number(d)] ?? d).join('');
export const sub = n => String(n).split('').map(d => SUB[Number(d)] ?? d).join('');
const minus = text => text.replace(/^-/, '−');
const clean = (value, digits) => {
  const fixed = value.toFixed(digits);
  return Number(fixed) === 0 ? (0).toFixed(digits) : fixed;
};
// Seis decimales fijos, como en las tablas de los ejercicios resueltos.
export const n6 = value => minus(clean(value, 6));
// Número compacto (sin ceros finales), hasta `digits` decimales.
export const ns = (value, digits = 6) => minus(String(Number(clean(value, digits))));
// Versión para TeX (signo menos ASCII, MathJax lo compone).
export const t6 = value => clean(value, 6);
export const ts = (value, digits = 6) => String(Number(clean(value, digits)));
export const paren = text => text.startsWith('-') ? `(${text})` : text;
export const sci = (value, digits = 2) => {
  if (value === 0) return '0';
  const exponent = Math.floor(Math.log10(Math.abs(value)));
  if (exponent >= -3 && exponent < 4) return ns(value, Math.max(0, digits + 1 - exponent));
  return `${minus((value / 10 ** exponent).toFixed(digits))}·10${String(exponent).replace('-', '⁻').split('').map(c => '⁰¹²³⁴⁵⁶⁷⁸⁹'['0123456789'.indexOf(c)] ?? c).join('')}`;
};
export const texSci = (value, digits = 2) => {
  if (value === 0) return '0';
  const exponent = Math.floor(Math.log10(Math.abs(value)));
  if (exponent >= -3 && exponent < 4) return ts(value, Math.max(0, digits + 1 - exponent));
  return String.raw`${(value / 10 ** exponent).toFixed(digits)}\times10^{${exponent}}`;
};
export function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (value == null || value === false) continue;
    if (key === 'text') node.textContent = value;
    else if (key === 'style') node.style.cssText = value;
    else node.setAttribute(key, value === true ? '' : value);
  }
  node.append(...children.filter(child => child != null));
  return node;
}
