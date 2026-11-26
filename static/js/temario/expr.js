// Analizador de expresiones matemáticas para los laboratorios del temario.
// No usa eval: convierte el texto en una función a partir de una gramática pequeña.
const FUNCTIONS = {
  sin: Math.sin, cos: Math.cos, tan: Math.tan, asin: Math.asin, acos: Math.acos, atan: Math.atan,
  sinh: Math.sinh, cosh: Math.cosh, tanh: Math.tanh, exp: Math.exp, sqrt: Math.sqrt, abs: Math.abs,
  ln: Math.log, log: Math.log, log10: Math.log10, sen: Math.sin,
};
const CONSTANTS = {pi: Math.PI, e: Math.E};

export class ExpressionError extends Error {}

function tokenize(text) {
  const tokens = [];
  const pattern = /\s*(?:(\d+\.?\d*(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?)|([A-Za-z_][A-Za-z_0-9]*)|(\*\*|[-+*/^(),]))/y;
  const source = text.replace(/[−–]/g, '-').replace(/[·×]/g, '*').replace(/π/g, 'pi');
  let index = 0;
  while (index < source.length) {
    if (/^\s*$/.test(source.slice(index))) break;
    pattern.lastIndex = index;
    const match = pattern.exec(source);
    if (!match) throw new ExpressionError(`Símbolo no reconocido: «${source.slice(index).trim()[0]}».`);
    if (match[1] !== undefined) tokens.push({type: 'number', value: Number(match[1])});
    else if (match[2] !== undefined) tokens.push({type: 'name', value: match[2]});
    else tokens.push({type: 'op', value: match[3] === '**' ? '^' : match[3]});
    index = pattern.lastIndex;
  }
  return tokens;
}

/** Devuelve una función `(…valores) => número` con las variables en el orden de `variables`. */
export function compile(text, variables = ['x']) {
  if (typeof text !== 'string' || !text.trim()) throw new ExpressionError('Escribe una expresión.');
  if (text.length > 200) throw new ExpressionError('La expresión es demasiado larga (máximo 200 caracteres).');
  const tokens = tokenize(text);
  let position = 0;
  const peek = () => tokens[position];
  const isOp = value => peek()?.type === 'op' && peek().value === value;
  const take = () => tokens[position++];

  function expression() {
    let left = term();
    while (isOp('+') || isOp('-')) {
      const operator = take().value, a = left, b = term();
      left = operator === '+' ? scope => a(scope) + b(scope) : scope => a(scope) - b(scope);
    }
    return left;
  }
  function term() {
    let left = unary();
    for (;;) {
      if (isOp('*') || isOp('/')) {
        const operator = take().value, a = left, b = unary();
        left = operator === '*' ? scope => a(scope) * b(scope) : scope => a(scope) / b(scope);
      } else if (peek() && (peek().type === 'name' || isOp('(')) && tokens[position - 1]?.type === 'number') {
        const a = left, b = unary();  // multiplicación implícita: 2x, 3(x+1)
        left = scope => a(scope) * b(scope);
      } else return left;
    }
  }
  function unary() {
    if (isOp('-')) { take(); const value = unary(); return scope => -value(scope); }
    if (isOp('+')) { take(); return unary(); }
    return power();
  }
  function power() {
    const base = atom();
    if (isOp('^')) { take(); const exponent = unary(); return scope => Math.pow(base(scope), exponent(scope)); }
    return base;
  }
  function atom() {
    const token = take();
    if (!token) throw new ExpressionError('La expresión está incompleta.');
    if (token.type === 'number') return () => token.value;
    if (token.type === 'name') {
      const name = token.value.toLowerCase();
      if (isOp('(') && FUNCTIONS[name]) {
        take();
        const argument = expression();
        if (!isOp(')')) throw new ExpressionError(`Falta cerrar el paréntesis de ${token.value}(…).`);
        take();
        const fn = FUNCTIONS[name];
        return scope => fn(argument(scope));
      }
      const slot = variables.indexOf(token.value);
      if (slot >= 0) return scope => scope[slot];
      if (name in CONSTANTS) return () => CONSTANTS[name];
      if (FUNCTIONS[name]) throw new ExpressionError(`Escribe el argumento entre paréntesis: ${token.value}(…).`);
      throw new ExpressionError(`«${token.value}» no es una variable ni una función conocida. Usa ${variables.join(', ')}.`);
    }
    if (token.value === '(') {
      const inner = expression();
      if (!isOp(')')) throw new ExpressionError('Falta cerrar un paréntesis.');
      take();
      return inner;
    }
    throw new ExpressionError(`No se esperaba «${token.value}» en esa posición.`);
  }

  const tree = expression();
  if (position < tokens.length) throw new ExpressionError(`No se esperaba «${tokens[position].value}» en esa posición.`);
  return (...values) => tree(values);
}
