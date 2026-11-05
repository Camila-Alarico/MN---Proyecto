"""Ejercicios originales: datos curados, no copias de ejercicios del libro."""
from .services.parser import parse_function, MathInputError
from .services.solving import run_method

TOPICS = {
    'errores': 'Errores y tolerancia',
    'biseccion': 'Bisección',
    'regla-falsa': 'Regla falsa',
    'punto-fijo': 'Punto fijo',
    'newton': 'Newton-Raphson',
    'secante': 'Secante',
    'raices-multiples': 'Raíces múltiples',
}
METHOD_KEYS = {'biseccion': 'bisection', 'regla-falsa': 'false-position', 'punto-fijo': 'fixed-point',
               'newton': 'newton', 'secante': 'secant', 'raices-multiples': 'multiple-roots'}
METHOD_TASKS = {
    'biseccion': ('Reduce un intervalo por la mitad.', r'm=\frac{a+b}{2}', 'm = (a + b)/2'),
    'regla-falsa': ('Conserva el cambio de signo y corta el eje con una recta entre los extremos.', r'x_r=a-\frac{f(a)(b-a)}{f(b)-f(a)}', 'xr = a − f(a)(b − a)/(f(b) − f(a))'),
    'newton': ('Usa la tangente y la primera derivada.', r'x_1=x_0-\frac{f(x_0)}{f\prime(x_0)}', 'x₁ = x₀ − f(x₀)/f′(x₀)'),
    'secante': ('Estima la pendiente con dos puntos, sin calcular la derivada.', r'x_2=x_1-\frac{f(x_1)(x_1-x_0)}{f(x_1)-f(x_0)}', 'x₂ = x₁ − f(x₁)(x₁ − x₀)/(f(x₁) − f(x₀))'),
    'punto-fijo': ('Evalúa una transformación equivalente x = g(x).', r'x_1=g(x_0)', 'x₁ = g(x₀)'),
    'raices-multiples': ('Corrige una raíz múltiple combinando f, su primera y su segunda derivada.', r'x_1=x_0-\frac{f(x_0)f\prime(x_0)}{[f\prime(x_0)]^2-f(x_0)f\prime\prime(x_0)}', 'x₁ = x₀ − f f′ / (f′² − f f″)'),
}
SOURCES = {
    'errores': ('Driscoll y Braun · Representación y errores', 'https://fncbook.com/floating-point/'),
    'biseccion': ('Kaw · Bisección', 'https://nm.mathforcollege.com/NumericalMethodsTextbookUnabridged/chapter-03.03-bisection-method-for-solving-a-nonlinear-equation.html'),
    'regla-falsa': ('MIT · Regla falsa', 'https://web.mit.edu/10.001/Web/Course_Notes/NLAE/node5.html'),
    'newton': ('Driscoll y Braun · Newton', 'https://fncbook.com/newton/'),
    'secante': ('Driscoll y Braun · Interpolación y secante', 'https://fncbook.com/secant/'),
    'punto-fijo': ('Driscoll y Braun · Punto fijo', 'https://fncbook.com/fixed-point/'),
    'raices-multiples': ('Driscoll y Braun · Newton y multiplicidad', 'https://fncbook.com/newton/'),
}
ERROR_CASES = [
    dict(v=10, approx=9.8, tolerance=.1, title='Pesa patrón en la balanza', level='Inicial', skill='medidas',
         context='Una balanza de laboratorio se calibra con una pesa patrón de 10 g y marca 9.8 g. El protocolo de calidad acepta una desviación de hasta 0.1 g. Decide si la balanza puede seguir en uso.'),
    dict(v=-5, approx=-4.9, tolerance=.05, title='Cámara de congelación', level='Inicial', skill='medidas',
         context='Una cámara de conservación debe mantenerse a −5 °C y su termómetro industrial marca −4.9 °C. El control de calidad tolera 0.05 °C de error absoluto. Trabaja con la referencia negativa y decide si la lectura es aceptable.'),
    dict(v=20, approx=19.5, tolerance=.5, title='Dosificador de reactivo', level='Inicial', skill='limites',
         context='Un dosificador debía entregar 20 L de reactivo y entregó 19.5 L. El procedimiento permite hasta 0.5 L de diferencia y acepta el valor límite. ¿La entrega cumple?'),
    dict(v=1250, approx=1248, tolerance=3, title='Altímetro de un dron', level='Aplicación', skill='escala',
         context='Un dron mide 1248 m sobre la cima de un cerro cuya altitud oficial es 1250 m. La tolerancia de navegación es de 3 m. Con cifras grandes, observa cuánto pesa realmente el error.'),
    dict(v=.04, approx=.039, tolerance=.002, title='Pipeta de microlitros', level='Aplicación', skill='escala',
         context='Una pipeta automática debe entregar 0.04 mL y el sistema registra 0.039 mL. La tolerancia es de 0.002 mL. Con cantidades tan pequeñas, el error absoluto parece despreciable; comprueba qué dice el relativo.'),
    dict(v=8, approx=8.125, tolerance=.1, title='Cronometraje manual', level='Inicial', skill='medidas',
         context='En una prueba de velocidad el tiempo oficial fue de 8 s y un cronometrista manual anotó 8.125 s. El reglamento acepta hasta 0.1 s de diferencia. La aproximación está por encima de la referencia: revisa que el error no lleve signo.'),
    dict(v=3.14159265359, approx=3.142, tolerance=.0005, title='π redondeado para un engrane', level='Aplicación', skill='representacion',
         context='Una hoja de cálculo redondeó π a tres decimales (3.142) para dimensionar un engrane. El diseño admite 0.0005 de error absoluto en la constante. Evalúa la aproximación obtenida por redondeo.'),
    dict(v=3.14159265359, approx=3.141, tolerance=.0005, title='π truncado en otro equipo', level='Aplicación', skill='representacion',
         context='Otro equipo descartó las cifras de π después del tercer decimal (3.141) con la misma tolerancia de 0.0005. Compara este caso con el redondeo: ¿truncar y redondear dan el mismo error?'),
    dict(v=100, approx=99.95, tolerance=.05, title='Resistencia de 100 Ω', level='Aplicación', skill='limites',
         context='Una resistencia nominal de 100 Ω se mide en 99.95 Ω y la especificación permite 0.05 Ω. Los valores decimales son datos exactos del ejercicio: decide qué ocurre justo en el límite.'),
    dict(v=0, approx=.0002, tolerance=.0001, title='Sensor de presión en reposo', level='Reto', skill='limites',
         context='Un sensor de presión debe indicar exactamente 0 mm de columna de agua en reposo, pero marca 0.0002 mm. La tolerancia absoluta es 0.0001 mm. Con referencia cero, razona qué medidas siguen teniendo sentido.'),
    dict(v=2500, approx=2495, tolerance=5, title='Odómetro en un recorrido largo', level='Aplicación', skill='escala',
         context='Un odómetro registra 2495 m en un tramo medido con cinta de 2500 m. La tolerancia del equipo es de 5 m. Anota el error relativo: lo compararás con otro ejercicio a menor escala.'),
    dict(v=2.5, approx=2.495, tolerance=.005, title='Pieza de precisión en centímetros', level='Aplicación', skill='escala',
         context='Una pieza de 2.5 cm se mide con un calibrador que indica 2.495 cm; la tolerancia es de 0.005 cm. Tiene la misma proporción de error que el odómetro, pero a otra escala: ¿es igual de aceptable?'),
    dict(v=.5, approx=.45, tolerance=.05, title='Dosis pediátrica', level='Reto', skill='escala',
         context='Una dosis pediátrica prescrita es de 0.5 mg y el equipo administró 0.45 mg. El protocolo acepta 0.05 mg de diferencia, pero la enfermería quiere saber además qué porcentaje de la dosis representa el error. Interpreta ambas cosas.'),
    dict(v=-120, approx=-118.5, tolerance=2, title='Sonda bajo el nivel del mar', level='Aplicación', skill='medidas',
         context='Una sonda submarina debía registrar una profundidad de −120 m (bajo el nivel del mar) y marcó −118.5 m. La tolerancia de posicionamiento es de 2 m. Cuida el signo de la referencia al calcular el relativo.'),
    dict(v=350, approx=352.1, tolerance=2, title='Tiempo de carga de una página', level='Reto', skill='limites',
         context='Un servidor debía responder en 350 ms y respondió en 352.1 ms. El acuerdo de servicio tolera 2 ms. La diferencia parece pequeña: compruébala frente al límite con cuidado.'),
]
ROOT_CASES = [
    dict(c=2, expression='x^2-2', title='Baldosa cuadrada de 2 m²', level='Inicial',
         context='Una baldosa cuadrada debe cubrir exactamente 2 m². Si x es el lado en metros, el área x² debe valer 2. Con el modelo f(x) = x² − 2 y 0 ≤ x ≤ 4, determina el lado.'),
    dict(c=3, expression='x^2-3', title='Grabado láser de 3 cm²', level='Inicial',
         context='Un láser debe grabar un cuadrado de 3 cm² sobre una pieza. Con x el lado en centímetros, el modelo es f(x) = x² − 3 y la máquina trabaja entre 0 y 4 cm. Determina el lado que debe programarse.'),
    dict(c=5, expression='x^2-5', title='Jardín de 5 dam²', level='Inicial',
         context='Un jardín cuadrado debe ocupar 5 dam² (1 dam = 10 m). Si x es el lado en decámetros, el modelo es f(x) = x² − 5 con 0 ≤ x ≤ 4. Calcula el lado y luego conviértelo a metros.'),
    dict(expression='x^3-x-2', title='Arista de un tanque con presupuesto fijo', level='Aplicación',
         context='El costo de fabricar un tanque cúbico de arista x (en decímetros) se modela con C(x) = x³ − x, y el presupuesto aprobado es 2 unidades. Encuentra la arista para la que C(x) = 2, es decir, la raíz de f(x) = x³ − x − 2.'),
    dict(expression='cos(x)-x', title='Ángulo de equilibrio de un brazo robótico', level='Aplicación',
         context='Un brazo robótico se autoajusta hasta que su ángulo x (en radianes) coincide con cos(x). Encuentra el ángulo de equilibrio, raíz de f(x) = cos(x) − x. Calcula con la calculadora en radianes.'),
    dict(expression='exp(-x)-x', title='Alarma de un monitor de concentración', level='Aplicación',
         context='La concentración de un fármaco decae como e^(−t) mg/L, con t en horas. El monitor dispara una alarma cuando esa concentración iguala el tiempo transcurrido t. Determina en qué instante ocurre, raíz de f(t) = e^(−t) − t.'),
    dict(expression='x*exp(x)-2', title='Índice de crecimiento bacteriano', level='Reto',
         context='En un cultivo, el índice de crecimiento x·e^x (con x en horas, 0 ≤ x ≤ 4) debe alcanzar el valor 2 para activar el siguiente paso del protocolo. Encuentra el instante x resolviendo f(x) = x·e^x − 2.'),
    dict(expression='x^3-2*x-5', title='Deflexión de una viga', level='Reto',
         context='Un modelo de ingeniería establece que la deflexión x (en centímetros, entre 0 y 4) de una viga cumple x³ − 2x − 5 = 0. Encuentra la deflexión resolviendo f(x) = x³ − 2x − 5.'),
]
FIXED_CASES = [
    dict(expression='cos(x)', reference='cos(x)-x', title='Seguimiento solar por iteración', level='Inicial', low=.25, high=1,
         context='Un seguidor solar corrige su ángulo repitiendo x ← cos(x) (en radianes) hasta estabilizarse. Parte de un ángulo inicial entre 0.25 y 1 y comprueba que la iteración se acerca a la solución de cos(x) = x.'),
    dict(expression='(x+2/x)/2', reference='x^2-2', title='Raíz de 2 sin calculadora', level='Aplicación', low=1, high=2,
         context='Para calcular √2 sin calculadora, un programa promedia x con 2/x en cada paso: x ← (x + 2/x)/2. Elige un inicio entre 1 y 2 y comprueba cuánto se acerca el primer paso a la solución de x² − 2 = 0.'),
    dict(expression='exp(-x)', reference='exp(-x)-x', title='Carga relativa en un circuito RC', level='Aplicación', low=.25, high=1,
         context='En un modelo simplificado de circuito RC, la carga relativa x cumple x = e^(−x). Se calcula con la iteración x ← e^(−x) partiendo de un valor entre 0.25 y 1. Evalúa el primer paso y su residuo.'),
    dict(expression='sqrt(2+x)', reference='x^2-x-2', title='Cadena de radicales', level='Reto', low=1, high=3,
         context='Un diseñador de patrones define una cadena de radicales con x ← √(2 + x), partiendo de un valor entre 1 y 3. La solución de la ecuación x² − x − 2 = 0 (la positiva) es el límite de la cadena. Comprueba el primer paso y su residuo.'),
]
MULTIPLE_CASES = [
    dict(expression=f'(x-{r})^2*(x+{r+1})', title=title, level='Aplicación', r=r, context=context)
    for r, title, context in (
        (1, 'Perfil de una pieza fresada', 'El perfil de una pieza fresada es p(x) = (x − 1)²(x + 2) (en mm). La herramienta de corte debe tocar la línea de referencia sin cruzarla en x = 1. Localiza ese punto con la corrección para raíces múltiples.'),
        (2, 'Trayectoria tangente de un dron', 'La altura de un dron respecto a una pared virtual sigue h(x) = (x − 2)²(x + 3) (en metros). Debe rozar la pared sin atravesarla en x = 2. Encuentra ese punto con la corrección para raíces múltiples.'),
        (3, 'Punto de equilibrio sin pérdidas', 'La ganancia neta de una línea de producción es g(x) = (x − 3)²(x + 4) (en miles de unidades). Se anula en x = 3 sin volverse negativa. Encuentra ese punto con la corrección para raíces múltiples.'),
    )
]


def cases(topic):
    return ERROR_CASES if topic == 'errores' else FIXED_CASES if topic == 'punto-fijo' else MULTIPLE_CASES if topic == 'raices-multiples' else ROOT_CASES


def exercise_case(state):
    return cases(state['topic'])[state['variant']]


def catalog():
    """Orden alternado: muestra variedad en las primeras tarjetas, permite filtrar."""
    return [dict(id=f'{topic}-{i}', topic=topic, method=title, number=i+1, **data)
            for i in range(max(len(cases(topic)) for topic in TOPICS)) for topic, title in TOPICS.items() for data in cases(topic)[i:i+1]]


def first_iteration(state, values):
    topic, data = state['topic'], exercise_case(state)
    _, answer = run_method(METHOD_KEYS[topic], dict(expression=data['expression'], tolerance=1e-6, max_iterations=1, **values), with_plot=False)
    if not answer['iterations']:
        raise MathInputError('El inicio ya es una raíz o no permite construir el paso. Elige otros datos para practicar la iteración. ' + answer['message'])
    return answer['iterations'][0]


def curve(state):
    data = exercise_case(state)
    f = parse_function(data['expression'])
    low, high = ((data['low'], data['high']) if state['topic'] == 'punto-fijo' else
                 (data['r']-.75, data['r']+.75) if state['topic'] == 'raices-multiples' else (0, 4))
    return [dict(x=low+(high-low)*i/64, y=f(low+(high-low)*i/64)) for i in range(65)]
