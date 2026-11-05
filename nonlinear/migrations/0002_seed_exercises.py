from django.db import migrations

EXERCISES = [
    ('biseccion', 'Para a=1 y b=2, ¿cuál es el punto medio Xm?', ['1.5', '1', '2', '3'], '1.5', 'Xm=(1+2)/2=1.5.'),
    ('biseccion', '¿Qué permite garantizar una raíz por bisección?', ['Continuidad y cambio de signo', 'Solo a < b', 'Derivada positiva'], 'Continuidad y cambio de signo', 'Una función continua con imágenes de signos opuestos tiene al menos una raíz dentro del intervalo.'),
    ('newton', 'Para f(x)=x²−2 y x₀=1, ¿cuál es el siguiente valor de Newton?', ['1.5', '2', '0'], '1.5', 'f(1)=−1 y f′(1)=2. Entonces x₁=1−(−1)/2=1.5.'),
    ('newton', '¿Cuál de estos métodos requiere derivada?', ['Newton-Raphson', 'Bisección', 'Secante'], 'Newton-Raphson', 'Newton utiliza f′(x). Secante aproxima la pendiente usando dos puntos.'),
    ('errores', 'Valor verdadero 10 y aproximado 9.8. ¿Error absoluto?', ['0.2', '0.02', '2'], '0.2', '|10−9.8|=0.2. El relativo es 0.02 y el porcentual es 2%.'),
    ('errores', 'Valor verdadero 0. ¿Qué ocurre con el error relativo?', ['No está definido', 'Siempre es cero', 'Es igual al absoluto'], 'No está definido', 'El error relativo divide entre |valor verdadero|. No se puede dividir entre cero.'),
    ('punto-fijo', '¿Cuál es la iteración de punto fijo?', ['x(n+1)=g(xn)', 'x(n+1)=f′(xn)', 'x(n+1)=a+b'], 'x(n+1)=g(xn)', 'El nuevo valor se obtiene evaluando g en el valor anterior.'),
    ('secante', '¿Cuántos puntos iniciales necesita secante?', ['2', '1', '3'], '2', 'La recta secante se construye a partir de dos aproximaciones.'),
    ('raices-multiples', '¿Qué raíz y multiplicidad tiene (x−1)³?', ['Raíz 1, multiplicidad 3', 'Raíz 3, multiplicidad 1', 'Raíz −1, multiplicidad 3'], 'Raíz 1, multiplicidad 3', 'El factor x−1 aparece tres veces: x=1 es raíz triple.'),
    ('conceptos', '¿Qué mide el residuo en una aproximación x?', ['|f(x)|', '|x|', 'El número de iteraciones'], '|f(x)|', 'El residuo |f(x)| mide cuánto falta para satisfacer la ecuación f(x)=0.'),
    ('regla-falsa', '¿Qué recta utiliza regla falsa?', ['La secante por los extremos', 'La tangente en el punto medio', 'La recta vertical x=0'], 'La secante por los extremos', 'La intersección de esa secante con el eje X determina xr.'),
    ('conceptos', '¿Un paso muy pequeño garantiza haber encontrado una raíz?', ['No, puede haber estancamiento', 'Sí, siempre', 'Solo si hay 100 iteraciones'], 'No, puede haber estancamiento', 'Hay que examinar también el residuo y los supuestos del método.'),
]


def seed(apps, schema_editor):
    exercise = apps.get_model('nonlinear', 'Exercise')
    for topic, statement, options, answer, explanation in EXERCISES:
        exercise.objects.get_or_create(statement=statement, defaults={'topic': topic, 'options': options,
                                     'correct_answer': answer, 'explanation': explanation})


class Migration(migrations.Migration):
    dependencies = [('nonlinear', '0001_initial')]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
