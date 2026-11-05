// Pure serialization shared by the download and reproducibility tests.
export function csvCell(value) {
  if (value == null) return '';
  let text = String(value);
  // Keep numerical cells numeric; expressions and other text must not become
  // spreadsheet formulas when the student opens the download.
  if (typeof value !== 'number' && /^[\s]*[=+\-@]/.test(text)) text = "'" + text;
  return /[",\r\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
}

export function buildCsv(method, meta, values, result, columns) {
  const cols = [...columns];
  if (!cols.some(([key]) => key === 'fx')) cols.push(['fx', 'g(x(n+1)) − x(n+1)']);
  cols.push(['formula', 'Fórmula del paso (valores mostrados redondeados)']);
  const residual = method === 'fixed-point' ? 'g(x(n+1)) − x(n+1)' : 'f(x(n+1))';
  const rows = [
    ['# NumLearn', meta.title],
    ['# funcion', values.expression],
    ...meta.parameters.map(key => [`# ${key}`, Number(values[key])]),
    ['# tolerancia', Number(values.tolerance)],
    ['# max_iteraciones', Number(values.max_iterations)],
    ['# estado', result.status],
    ['# mensaje', result.message],
    ['# nota', `Paso |Δx| no es el error real. El residuo con signo es ${residual}; su magnitud es el valor absoluto. La cota de Bisección requiere continuidad y cambio de signo.`],
    cols.map(([, label]) => label),
    ...result.iterations.map(row => cols.map(([key]) => row[key])),
  ];
  return '\uFEFF' + rows.map(row => row.map(csvCell).join(',')).join('\r\n');
}

export function configurationUrl(baseUrl, values, parameters) {
  const query = new URLSearchParams();
  for (const key of ['expression', 'tolerance', 'max_iterations', ...parameters]) {
    query.set(key, values[key]);
  }
  return `${baseUrl}?${query}`;
}
