# NumLearn — documentación técnica v2.0

**Noviembre de 2026 · Grupo 2 · Ingeniería de Sistemas, UNSA**

## 1. Descripción

NumLearn es un laboratorio web para aprender Métodos Numéricos mediante teoría breve, ejemplos resueltos, calculadoras, laboratorios interactivos, prácticas guiadas y autoevaluaciones. La organización académica visible comprende siete unidades, sin usar las semanas del sílabo como niveles de navegación:

1. Errores.
2. Aproximación.
3. Raíces de ecuaciones.
4. Sistemas de ecuaciones lineales.
5. Ajuste de curvas e interpolación.
6. Integración y derivación numérica.
7. Ecuaciones diferenciales.

## 2. Arquitectura

- **Backend:** Python y Django 5.2. Las aplicaciones separan el curso (`temario`), las raíces y sus prácticas (`nonlinear`), los sistemas lineales (`linear`), y la evaluación y puntuación (`assessment`). `core` reúne páginas y configuración transversal.
- **Presentación:** Django Templates en `templates/`, estilos en `static/css/` y JavaScript ES modules en `static/js/`. Se utilizan Bootstrap/Bootstrap Icons, MathJax y Plotly donde corresponde; no se incorpora React, Vue ni otro framework SPA.
- **Temario:** `temario/catalog.py` define las unidades y lecciones; `temario/navigation.py` vincula cada unidad con su autoevaluación. Las páginas conservan URLs propias.
- **Evaluación:** `assessment/bank.py` declara las preguntas y fuentes; `assessment/generators.py` genera datos reproducibles por semilla; `assessment/engine.py` compone intentos, presenta etapas y valida respuestas en el servidor; `assessment/scoring.py` calcula el puntaje por unidad y el acumulado.
- **Persistencia:** Django ORM guarda intentos y respuestas en PostgreSQL en producción. SQLite está disponible como alternativa explícita para desarrollo. La puntuación se deriva de los intentos guardados; estos cambios no requieren migraciones.
- **Despliegue:** `vercel.json` configura el proyecto Django para Vercel; `scripts/build_vercel.py` prepara la compilación. La configuración de producción requiere `SECRET_KEY` y una URL de PostgreSQL.

## 3. Funcionalidades base del proyecto

- Lecciones, teoría, navegación del curso, avance de temas y acceso para estudiantes invitados.
- Calculadoras y simuladores de métodos de raíces: bisección, regla falsa, punto fijo, Newton-Raphson, secante y raíces múltiples.
- Formulación y solución de sistemas lineales con eliminación gaussiana y Gauss-Seidel.
- Exploración de errores, representación numérica, propagación, tolerancias y visualización de iteraciones.
- Prácticas guiadas, ejemplos resueltos, animaciones educativas y exportación/consulta de resultados.
- Registro de intentos y respuestas, con indicadores de integridad que no se interpretan por sí solos como prueba de conducta indebida.

## 4. Mejoras de esta versión

### 4.1 Curso y navegación

Se consolida el recorrido en siete unidades, presentadas como unidades temáticas y no como semanas. Las unidades 2, 5, 6 y 7 incorporan ahora autoevaluación, además de las evaluaciones que ya existían para Errores, Raíces y Sistemas lineales.

### 4.2 Evaluación por etapas en los siete módulos

Cada unidad tiene un alcance propio y un banco de problemas `STEPS`. Los nuevos bancos incorporan dos problemas por unidad:

- **Aproximación:** aproximación de Taylor y redondeo/exactitud.
- **Ajuste de curvas:** ajuste lineal e interpolación.
- **Integración y derivación:** regla trapezoidal y diferencia central.
- **Ecuaciones diferenciales:** Euler y Euler modificado.

Los problemas se generan con datos variables y una semilla almacenada en el intento. Cada problema contiene etapas encadenadas: el servidor no permite responder una etapa posterior antes de validar la actual. Se mantienen los tres intentos por etapa y la escala de crédito parcial ya implementada. Los tipos antiguos de pregunta continúan soportados para intentos existentes.

### 4.3 Puntaje acumulativo

`assessment/scoring.py` calcula el mejor intento terminado de cada unidad. Cada problema contribuye según el promedio de sus etapas; el porcentaje de unidad se calcula sobre el total de problemas. El puntaje acumulado es el promedio simple de las unidades que el estudiante ya rindió y que tienen evaluación disponible. Una unidad pendiente o todavía no evaluada no se registra como cero. Las evaluaciones conjuntas no duplican el resultado de las evaluaciones individuales.

Al añadir las cuatro unidades faltantes a `temario/navigation.py`, quedan representadas las siete unidades en el cálculo acumulado, sin alterar el esquema de base de datos.

### 4.4 Errores y revisión

La explicación de resultados en Recursos distingue explícitamente el tamaño del paso, el residuo y la cota de error. Son magnitudes diferentes y ninguna debe presentarse automáticamente como error verdadero. Se conserva el punto intermedio de la práctica de errores: primero se solicita la diferencia con signo entre referencia y aproximación y luego se calcula el error absoluto; cada campo se valida por separado.

Se corrige el texto de la práctica que identifica el método Newton-Raphson y se fija `1e-6` como tolerancia inicial en los formularios, calculadoras y ejemplos de métodos de raíces donde antes se proponía `1e-4`. Los valores que describen experimentos de truncamiento, derivación o límites numéricos no se cambian cuando no son tolerancias por defecto.

### 4.5 Footer

El footer identifica al Grupo 2 en una cuadrícula 2×2 que pasa a una columna en móvil. Añade la versión, fecha, crédito de asistencia de IA y un enlace reservado al portal común (`#portal-comun`).

## 5. Pruebas y verificación

La verificación prevista es `python manage.py test`, que ejecuta las pruebas Django de las aplicaciones. En el entorno donde se preparó esta entrega, el comando se intentó ejecutar, pero no pudo iniciar porque Django no está instalado (`ModuleNotFoundError: No module named 'django'`). La instalación de `requirements.txt` tampoco fue posible porque el entorno no tuvo acceso a la red de paquetes. Como comprobación adicional, los módulos Python modificados pasaron `python -m compileall` y se comprobaron de forma independiente los ocho generadores nuevos con 200 semillas; todos produjeron problemas válidos y variación de datos. Por tanto, no se declara que la suite Django haya pasado: debe ejecutarse en un entorno con las dependencias del proyecto instaladas.

No se añadieron dependencias ni migraciones.

## 6. Bibliografía y recursos

- Burden, R. L., y Faires, J. D. (2011). *Numerical Analysis* (9.ª ed.). Brooks/Cole.
- Chapra, S. C., y Canale, R. P. (2015). *Numerical Methods for Engineers* (7.ª ed.). McGraw-Hill Education.
- Driscoll, T. A., y Braun, R. J. *Fundamentals of Numerical Computation*. https://fncbook.com/
- Django Software Foundation. *Django documentation*. https://docs.djangoproject.com/
- Vercel. *Django on Vercel*. https://vercel.com/docs/frameworks/backend/django

Los problemas nuevos son ejercicios originales del proyecto construidos a partir de los conceptos y métodos cubiertos por estas referencias.

## 7. Créditos

**Grupo 2 — Universidad Nacional de San Agustín de Arequipa, Escuela Profesional de Ingeniería de Sistemas**

- Alarico Pacheco Camila Fernanda.
- Ayque Puraca Tania Luz.
- Barra Quispe Fernando Jonathan.
- Ore Soto Andres Raul.

**Asistencia de IA:** se utilizó asistencia de inteligencia artificial para apoyar la implementación, revisión de código, elaboración de problemas por etapas y redacción de esta documentación. La selección de contenidos, integración del proyecto y validación final corresponden al equipo. La asistencia de IA no sustituye la revisión académica ni la responsabilidad de sus integrantes.
