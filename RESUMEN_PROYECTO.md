# NumLearn — guía del proyecto y estado actual

Fecha de revisión: **29 de octubre de 2026**.

**Entrega centrada en Errores numéricos, 29/10/2026:** la portada y la navegación
principal llevan a teoría, práctica y evaluación de ese único tema. La teoría
se divide en Conceptos y medidas, Origen del error y Explorador. Hay **12 ejercicios
de errores** y **20 preguntas**, con cinco de conceptos y cinco de aplicación por
intento. La meta es ocho aciertos de diez.

Los otros temas y sus calculadoras se conservan como material secundario. Las
funciones de cálculo no se simplificaron. Los intentos de Errores no recuperan
actividades mezcladas anteriores. Véanse el [recorrido y sus límites](docs/UX_APRENDIZAJE.md)
y el [fundamento académico](docs/FUNDAMENTO_ERRORES.md).

NumLearn es una página educativa de métodos numéricos. Permite estudiar teoría,
resolver problemas, consultar el procedimiento y comparar resultados. Actualmente
tiene dos módulos disponibles: ecuaciones no lineales y sistemas lineales. El
programa anuncia cinco módulos en total; los otros tres están pendientes.

Este documento explica qué encuentra el estudiante en la página, para qué sirve
cada módulo y cómo está organizado el código para los próximos cambios.

Contenido:

- [Estado de la versión](#estado-desde-el-que-se-harán-los-cambios).
- [Prioridad después de la retroalimentación](#prioridad-después-de-la-retroalimentación).
- [Los cinco módulos](#qué-incluye-la-página).
- [Cómo usar la página](#cómo-se-recorre-la-página).
- [Cuentas y funciones generales](#cuentas-y-funciones-generales).
- [Estructura y archivos](#cómo-está-construido-y-dónde-cambiar-cada-cosa).
- [Rutas](#rutas-para-orientarse).
- [Ejecución y pruebas](#ejecutar-y-comprobar).
- [Puntos antes de modificar](#puntos-presentes-antes-de-modificar).

## Estado desde el que se harán los cambios

| Dato | Estado |
| --- | --- |
| Carpeta local | `/home/tniia/tania/u/6/mn/paginaweb` |
| Repositorio | [tniia/metodos-numericos](https://github.com/tniia/metodos-numericos) |
| Rama de trabajo | `feat/laboratorio-metodos-numericos` |
| Commit base de esta revisión | `6fe5280` — «agregando cosas», firmado por Andrés |
| GitHub y copia local | El 29/10/2026 se consultó GitHub y se actualizó la copia local hasta ese commit, sin conflictos. |
| Revisión posterior del 29/10/2026 | Nueva UX, práctica, autoevaluación y LaTeX; consultar `git log -1` para su commit. |
| Configuración local | Existen `.env`, `.venv` y `db.sqlite3`. |
| Revisión del 29/10/2026 | Django no informa problemas en `manage.py check`; todas las migraciones figuran aplicadas. |

El proyecto actual parte de `numlearn-sistemas-lineales (1).zip`, que reemplazó
la versión anterior del repositorio. Después se corrigió la ejecución local y un
problema de resultados desactualizados (`675a2c4`). La versión más reciente también
incluye dos commits posteriores, subidos el 22/10/2026 e incorporados a esta copia
el 29/10/2026:

- `2304fef`: ruta de aprendizaje por familias, selector de método y ejercicios
  resueltos. Autor registrado: NumLearn; commit realizado por Andrés.
- `6fe5280`: Andrés añadió `ruta-aprendizaje-y-ejercicios-resueltos.patch`.
  El parche guarda cambios que ya están incorporados; no hace falta aplicarlo otra vez.

La retroalimentación de la profesora define el objetivo de la siguiente entrega.
El trabajo actual se centra en terminar el tema de Errores numéricos con un recorrido coherente.

## Prioridad después de la retroalimentación

La indicación registrada para la siguiente clase es **elegir un módulo y
terminarlo bien**, con pocas experiencias educativas completas. Tener una
calculadora disponible no significa que el módulo ya cumpla ese objetivo.

Se conservaron por separado las [observaciones proporcionadas por el equipo](RETROALIMENTACION_PROFESORA.md)
y una [revisión frente al código actual, con prioridades propuestas](REVISION_RETROALIMENTACION.md).

La página tiene teoría, gráficas, ejemplos, comparación y pivoteo parcial en
Gauss. La revisión local añade **práctica con respuestas del estudiante**:
identificar el problema y el método, preparar datos, calcular y comprobar.
La entrega principal incorpora un banco de 20 preguntas de errores, con diez por intento.

La navegación principal separa Teoría, Práctica guiada, Autoevaluación y Recursos,
con el tema de Errores como referencia. Los demás temas tienen acceso secundario. Se retiraron de la navegación Ingresar, progreso,
favoritos y apuntes; sus rutas y datos anteriores se conservan. Las pestañas muestran un panel a la vez. La búsqueda admite
peticiones breves como «Quiero Newton».

El foco acordado con el equipo es **Errores numéricos**, un solo tema. La
profesora habló de completar un módulo; el equipo decidió acotar esta entrega
al tema de errores. Los demás métodos son contenido complementario; los módulos
3–5 siguen pendientes. Las calculadoras conservan sus funciones.


También se pide documentar el uso de IA; el trabajo de esta revisión está registrado
en `docs/UX_APRENDIZAJE.md`, pendiente de complementar con el historial del equipo.

## Qué incluye la página

| Módulo | Pregunta que aborda | Estado real |
| --- | --- | --- |
| 1. Ecuaciones no lineales y errores | ¿Qué valor hace que una función sea cero y cómo evalúo una aproximación? | Disponible: teoría, seis métodos, comparador; entrega centrada en errores con 12 ejercicios y autoevaluación propia. |
| 2. Sistemas de ecuaciones lineales | ¿Qué valores satisfacen varias ecuaciones a la vez? | Disponible: Gauss, Gauss-Seidel y comparación para 2×2 y 3×3. |
| 3. Interpolación y ajuste de curvas | ¿Cómo obtengo una función a partir de datos? | Anunciado; sin calculadora ni páginas de cálculo propias. |
| 4. Integración numérica | ¿Cómo aproximo una integral mediante evaluaciones de una función? | Anunciado; sin calculadora ni páginas de cálculo propias. |
| 5. Ecuaciones diferenciales | ¿Cómo aproximo una evolución a partir de una tasa de cambio y un dato inicial? | Anunciado; sin calculadora ni páginas de cálculo propias. |

### Módulo 1: ecuaciones no lineales y errores

Busca soluciones de **f(x) = 0**, llamadas raíces. Por ejemplo, para
`f(x) = x³ − x − 2`, una raíz es aproximadamente `1.521380`: al sustituirla, el
resultado queda cerca de cero. Los métodos calculan aproximaciones sucesivas a
esa raíz y permiten estudiar su comportamiento.

La ruta de aprendizaje organiza el contenido en seis pasos:

1. **Errores numéricos:** medir una aproximación y entender la tolerancia.
2. **Raíces de ecuaciones:** comprender qué significa resolver `f(x) = 0`.
3. **Métodos cerrados:** bisección y regla falsa.
4. **Métodos abiertos:** Newton, punto fijo, secante y Newton modificado.
5. **Raíces múltiples de polinomios:** distinguir raíces simples y repetidas.
6. **Comparar métodos:** contrastar recorridos y resultados.

**Errores y precisión.** La página permite introducir un valor de referencia y
uno aproximado. Calcula error absoluto, relativo y porcentual, muestra la
sustitución numérica y permite mover la aproximación con un control deslizante.
También se puede cambiar la tolerancia y observar si la aproximación la cumple.

Por ejemplo, con referencia `10` y aproximación `9.8`, el error absoluto es
`0.2`, el relativo `0.02` y el porcentual `2 %`. Con tolerancia absoluta `0.1`,
esa aproximación todavía no cumple. Si la referencia es cero, el error relativo
no está definido. Cambiar los decimales que se muestran no mejora el valor calculado.

**Los seis métodos disponibles:**

| Método | Datos iniciales | Cómo trabaja | Qué conviene observar |
| --- | --- | --- | --- |
| Bisección | Función y extremos `a`, `b`. | Divide el intervalo por la mitad y conserva el cambio de signo. | Su cota de error supone continuidad y un intervalo adecuado. |
| Regla falsa | Función y extremos `a`, `b`. | Usa el corte con el eje de la recta entre los extremos. | Puede avanzar lentamente si uno de los extremos queda fijo. |
| Punto fijo | Transformación `g(x)` y punto `x₀`. | Repite `x siguiente = g(x actual)`. | La transformación elegida puede hacer que converja o diverja. |
| Newton-Raphson | Función y punto `x₀`. | Usa la derivada para calcular el corte de la tangente con el eje. | Una derivada nula o un punto inicial inadecuado pueden impedir el avance. |
| Secante | Función y puntos `x₀`, `x₁`. | Aproxima la pendiente con los dos últimos puntos. | No exige introducir derivadas y puede salir del intervalo inicial. |
| Newton modificado para raíces múltiples | Función y punto `x₀`. | Usa la función y sus dos primeras derivadas para tratar raíces repetidas. | El procedimiento cambia respecto al Newton ordinario y también necesita validaciones numéricas. |

En todos se configura la tolerancia y el máximo de iteraciones. El servidor
calcula las derivadas cuando el método las necesita. La interfaz muestra los
campos correspondientes al método seleccionado.

En punto fijo, la expresión del simulador representa **g(x)**. No se debe pegar
una `f(x)` cualquiera y esperar que resuelva `f(x) = 0`: primero hay que construir
una transformación equivalente. Por ejemplo, `x³ − x − 2 = 0` puede reescribirse
como `x = (x + 2)^(1/3)`. El comparador distingue la función original y la
transformación para comprobar también el residuo original.

**Qué muestra el simulador.** Hay una gráfica de la función y de la construcción
del método, una tabla de iteraciones, fórmulas con los valores sustituidos,
un estado final y una gráfica del residuo. Se puede avanzar, retroceder,
reproducir automáticamente, seleccionar una iteración, ajustar el rango visual,
exportar la tabla a CSV y copiar un enlace con la configuración.

La tolerancia es el umbral elegido para aceptar el cálculo. El paso es el cambio
entre aproximaciones y el residuo es `|f(x)|`; en punto fijo es `|g(x) − x|`.
Son datos distintos del error real `|x − raíz verdadera|`. La parada considera
el paso y el residuo, con particularidades como la cota de intervalo de bisección.

**Polinomios y raíces múltiples.** La lección usa
`p(x) = (x − 1)²(x + 2)`: `−2` es una raíz simple y `1` es doble. Permite estudiar
por qué una raíz puede tocar el eje sin cambiar de signo y por qué Newton puede
volverse más lento. Hay enlaces a escenarios precargados. No es una calculadora
general que enumere automáticamente todas las raíces reales y complejas de un polinomio.

**Búsqueda gráfica.** Es una herramienta de apoyo, fuera de los seis pasos de la
ruta. Recibe una función y un intervalo, dibuja muestras y distingue puntos
evaluados con valor cero de intervalos candidatos con cambio de signo. Desde
estos últimos se puede pasar a bisección. El muestreo no demuestra continuidad
ni garantiza encontrar todas las raíces.

**Comparador.** Ejecuta varios métodos sobre el problema configurado y muestra
aproximaciones, iteraciones, residuos, errores respecto a una raíz de referencia,
análisis de convergencia y diferencias entre recorridos. Esa referencia puede
ser estimada numéricamente: no siempre es una solución exacta conocida.
Los tiempos del servidor tampoco determinan por sí solos qué método conviene.

### Módulo 2: sistemas de ecuaciones lineales

Busca valores que satisfagan varias ecuaciones simultáneamente. La forma
**A·x = b** organiza los coeficientes en una matriz `A`, las incógnitas en `x`
y los términos independientes en `b`. En esta página se admiten sistemas
**2×2 y 3×3**, con números reales finitos.

Su ruta tiene cuatro pasos: **formulación y convergencia → métodos directos →
métodos iterativos → comparación**. El selector permite pasar entre Gauss y
Gauss-Seidel conservando la matriz y el vector; actualmente no transporta la
tolerancia ni el máximo de iteraciones al cambiar de página.

| Método | Cómo trabaja | Qué muestra |
| --- | --- | --- |
| Eliminación gaussiana con pivoteo parcial | Elige pivotes por magnitud, intercambia filas si hace falta, elimina términos y resuelve hacia atrás. | Matriz aumentada, pivotes, multiplicadores, matrices intermedias, sustituciones y verificación. |
| Gauss-Seidel | Parte del vector cero y actualiza cada incógnita usando los valores más recientes. | Tabla de aproximaciones, tamaño del paso, residuo por iteración y estado de convergencia. |

El ejemplo principal interpreta las incógnitas como índices de demanda de tres
servicios. Es didáctico: no documenta datos reales de una organización.

```text
4x₁ +  x₂ +  x₃ =  9
 x₁ + 5x₂ +  x₃ = 14
 x₁ +  x₂ + 6x₃ = 21

Solución: (1, 2, 3).
Gauss: residuo 0 en este ejemplo.
Gauss-Seidel: 8 iteraciones con la configuración base.
```

En Gauss-Seidel, la primera iteración desde cero produce aproximadamente
`(2.25, 2.35, 2.733333)`. Las siguientes se acercan a `(1, 2, 3)`.
El caso base usa tolerancia `10⁻⁶` y un máximo de 100 iteraciones. La parada exige
que tanto el paso como el residuo estén dentro de la tolerancia.

La dominancia diagonal estricta por filas garantiza la convergencia de
Gauss-Seidel; es suficiente, pero no necesaria. La página incluye contrastes:

| Ejemplo incluido | Qué se aprende |
| --- | --- |
| Caso base | Ambos métodos obtienen resultados compatibles. |
| Las mismas ecuaciones en otro orden | Gauss intercambia filas y resuelve; Gauss-Seidel diverge con ese orden. |
| Sistema 2×2 sin dominancia diagonal estricta | Gauss-Seidel puede converger aunque no se cumpla esa condición suficiente. |
| Filas `(1, 2)` y `(2, 4)`, con `b = (3, 6)` | Hay infinitas soluciones, por lo que no existe una solución única que presentar. |

La comparación muestra soluciones, residuos, procedimiento y diferencia entre
ambas respuestas. Un residuo pequeño significa que las ecuaciones casi se
cumplen; en un sistema mal condicionado no garantiza un error pequeño en `x`.
La aritmética es de punto flotante, también en el método directo.

### Módulo 3: interpolación y ajuste de curvas

**Estado: pendiente.** Existe su entrada en el programa, pero todavía no hay
pantallas ni algoritmos de este módulo en la aplicación.

Su propósito sería obtener una función a partir de datos. Son dos tareas distintas:
la **interpolación** construye una función que pasa por los puntos dados; el
**ajuste** busca una tendencia y puede dejar diferencias respecto a las mediciones.

El catálogo anuncia **interpolación de Lagrange y regresión lineal**.
Un ejemplo conceptual sería usar mediciones de tiempo y temperatura para estimar
un valor intermedio o describir su tendencia. Ese ejemplo explica el tema;
actualmente no puede ejecutarse desde este módulo en NumLearn.

### Módulo 4: integración numérica

**Estado: pendiente.** Solo aparece anunciado en el programa del curso.

Su propósito sería aproximar una integral definida a partir de evaluaciones de
la función. Por ejemplo, integrar una velocidad respecto al tiempo permite
calcular desplazamiento. En otros problemas representa acumulación o área con signo.

El catálogo anuncia **trapecio compuesto y Simpson compuesto**. Para una
calculadora de estos métodos harían falta, entre otros datos, una función,
los límites de integración y una partición. Estos campos describen el problema
matemático; todavía no existen como formulario implementado en este módulo.

### Módulo 5: ecuaciones diferenciales

**Estado: pendiente.** No tiene simuladores implementados.

Estudiaría problemas en los que se conoce cómo cambia una cantidad, por ejemplo
`y′ = f(t, y)`, y un valor inicial `y(t₀) = y₀`. El resultado es una trayectoria
aproximada en varios puntos, en lugar de una única raíz.

El catálogo anuncia **Euler explícito y Runge-Kutta de orden 4**. Un ejemplo
conceptual es el crecimiento `y′ = y`, con `y(0) = 1`. Para aproximarlo se elige
un paso y se avanza desde el dato inicial. Es una explicación de lo previsto,
no una función disponible en la página actual.

## Cómo se recorre la página

La portada presenta el programa y los accesos a los módulos disponibles. La
barra lateral organiza los recorridos y el buscador permite encontrar temas de
ambos módulos, sin distinguir mayúsculas ni tildes. Los módulos pendientes pueden
aparecer en el catálogo, pero no tienen un laboratorio al que entrar.

Un recorrido de uso puede ser:

1. Entrar al módulo y leer el fundamento del tema.
2. Abrir el simulador de una familia y elegir un método.
3. Revisar su ejercicio resuelto y pulsar **Reproducir en el simulador** para
   cargar los datos; después ejecutar el cálculo.
4. Consultar los pasos y comparar la tabla con el ejercicio explicado.
5. Modificar un dato y observar qué cambia en la aproximación o la convergencia.
6. Abrir el comparador para contrastar métodos sobre el mismo problema.
7. Practicar con respuestas propias y comprobar conceptos en la autoevaluación.

El selector de raíces conserva los parámetros compatibles entre métodos. Al
entrar o salir de punto fijo no copia la expresión como si `f(x)` y `g(x)` fueran
lo mismo. En ambos módulos se conservan las direcciones propias de cada método.

Los ejercicios resueltos de Andrés contienen planteamiento, tabla y conclusión;
se conservan como ejemplos. La **práctica guiada principal trabaja errores**: pide respuestas y valida
cada paso en el servidor. La **autoevaluación** cuenta la primera respuesta de
diez preguntas de errores elegidas de un banco de 20 y explica los fallos. La meta de ese
intento es ocho aciertos; no certifica el dominio de todos los métodos.

El quiz antiguo y sus modelos se eliminaron con el ZIP. Las actividades nuevas
usan sesiones, no recuperan intentos antiguos ni guardan notas permanentes por
alumno. Recargar permite continuar el intento actual.

## Cuentas y funciones generales

En la interfaz actual se retiraron los accesos personales y las marcas manuales.
La tabla siguiente describe funciones heredadas que conservan sus datos y rutas;
no todas están ofrecidas en la navegación de la entrega.

| Función | Qué permite | Cuenta necesaria |
| --- | --- | --- |
| Lecciones y calculadoras | Leer contenidos, resolver y comparar problemas. | No. |
| Práctica guiada y autoevaluación | Resolver pasos y comprobar conocimientos; el intento se conserva en la sesión. | No. |
| Búsqueda global | Encontrar temas y módulos del catálogo. | No. |
| Progreso | Marcar contenidos completados y ver el avance de la ruta. | No para conservarlo en la sesión; sí para asociarlo a una cuenta. |
| Historial | Guardar automáticamente cálculos y reabrir sus datos. | Sí. |
| Favoritos | Destacar cálculos del historial. | Sí. |
| Apuntes | Crear y eliminar notas personales. | Sí. |
| Registro y acceso | Crear una cuenta, entrar y salir. | Son los mecanismos para acceder a las funciones personales. |
| Recuperación de contraseña | Solicitar un enlace para restablecer el acceso. | Requiere una cuenta y configuración de correo para entrega real. |

El progreso de invitado se guarda en la sesión y se incorpora a la cuenta al
iniciar sesión o registrarse. La ruta agrupa métodos: completar cualquiera de
los de una familia completa ese paso de la ruta. La marca es manual; no acredita
que el estudiante haya aprobado una evaluación ni dominado todos los métodos.

Los cálculos de raíces se guardan con su configuración. En sistemas lineales,
el enlace del historial vuelve a cargar la matriz y el vector; no restaura
actualmente todos los parámetros iterativos. El historial y los apuntes son personales.

La recuperación de contraseña usa correo de consola por defecto; el envío real
requiere configurar correo. El asistente de la interfaz usa mensajes programados,
sin un servicio de IA externo.

La sección **Recursos** explica cómo escribir funciones e interpretar resultados.
Se usa `x`, multiplicación explícita como `2*x`, potencias como `x^3`, logaritmo
natural y ángulos en radianes. El panel `/admin/` corresponde a la administración
de Django y requiere una cuenta con permisos de administración.

## Cómo está construido y dónde cambiar cada cosa

El servidor usa **Python y Django 5.2**. La interfaz usa plantillas Django, CSS y
JavaScript con módulos ES. Bootstrap, Bootstrap Icons y Plotly se cargan desde
CDN; MathJax 3.2.2 y las fuentes tipográficas se sirven localmente. No necesita compilar
un frontend para ejecutarse.

SymPy ayuda con las expresiones matemáticas. PostgreSQL es la base prevista para
producción; SQLite está habilitado explícitamente para desarrollo local.
WhiteNoise sirve archivos estáticos y Gunicorn es el servidor configurado para producción.

| Qué se quiere cambiar | Archivos o carpetas principales |
| --- | --- |
| Configuración y rutas generales | `config/settings.py`, `config/urls.py` |
| Portada y módulos disponibles | `templates/core/home.html`, `core/catalog.py` |
| Menús y estructura común | `templates/base.html`, `templates/components/` |
| Estilos | `static/css/` |
| Temas, familias, ruta y ejercicios resueltos del módulo 1 | `nonlinear/catalog.py`: `METHODS`, `FAMILIES`, `ROUTE`, `WORKED_EXAMPLES` |
| Cálculo de raíces y comparador | `nonlinear/services/` |
| Interfaz de raíces y comparación | `templates/nonlinear/`, `static/js/nonlinear/` |
| Temas, familias, ruta y ejemplos de sistemas lineales | `linear/catalog.py`: `METHODS`, `FAMILIES`, `ROUTE`, `WORKED_EXAMPLES` |
| Gauss y Gauss-Seidel | `linear/services/direct.py`, `linear/services/iterative.py` |
| Validación y ejecución de sistemas | `linear/forms.py`, `linear/services/solving.py` |
| Interfaz de sistemas lineales | `templates/linear/`, `templates/components/linear_lab.html`, `static/js/linear/lab.js` |
| Presentación común de ejercicios resueltos | `templates/components/worked_example.html` |
| Cuentas, progreso, apuntes y búsqueda | `core/` |
| Pruebas de Django | `core/tests.py`, `linear/tests.py` |
| Pruebas de JavaScript y navegador | `tests/javascript-syntax.test.cjs`, `tests/browser/linear.spec.cjs` |
| Verificación en GitHub | `.github/workflows/tests.yml` |
| Configuración de despliegue | `render.yaml`, `Procfile` |

Los formularios validan entradas, las vistas atienden las peticiones y los
servicios realizan el cálculo. El navegador envía JSON a la API y presenta la
respuesta. Conviene mantener esa distribución al modificar algoritmos o pantallas.

Los datos persistentes propios son `UserProgress`, `StudyNote` y
`CalculationHistory`, además de los modelos de cuentas de Django. El módulo lineal
reutiliza el historial con los identificadores `linear-gauss`, `linear-seidel`
y `linear-compare`.

`index.html`, `css/` y `js/` corresponden al prototipo anterior. La página actual
se ejecuta con Django; abrir ese `index.html` no muestra la plataforma completa.

## Rutas para orientarse

| Ruta | Contenido |
| --- | --- |
| `/` | Portada y programa del curso |
| `/ecuaciones-no-lineales/` | Índice de teoría del módulo 1 |
| `/ecuaciones-no-lineales/teoria/` | Teoría y temas |
| `/ecuaciones-no-lineales/practica/` | Tres actividades guiadas |
| `/ecuaciones-no-lineales/autoevaluacion/` | Ocho preguntas por intento |
| `/ecuaciones-no-lineales/<slug>/` | Lección o simulador, por ejemplo `newton/` o `comparar/` |
| `/sistemas-lineales/` | Índice del módulo 2 |
| `/sistemas-lineales/formulacion/` | Explicación del sistema y convergencia |
| `/sistemas-lineales/eliminacion-gaussiana/` | Calculadora de Gauss |
| `/sistemas-lineales/gauss-seidel/` | Calculadora de Gauss-Seidel |
| `/sistemas-lineales/comparacion-metodos/` | Comparador lineal |
| `/buscar/?q=Gauss` | Búsqueda global |
| `/mi-progreso/`, `/mis-apuntes/`, `/favoritos/` | Información de la cuenta |
| `/health/` | Comprobación de salud del servidor |

Las API de cálculo reciben **POST con JSON** y protección CSRF:
`/api/nonlinear/<method>/` y `/api/linear/<method>/`.
Ambos módulos tienen rutas auxiliares `compare/` y `progress/`; el módulo 1
también tiene `graph/` y `errors/`.

Los enlaces antiguos `laboratorio/?method=...` redirigen a la página del método.
Los catálogos de cada módulo definen sus nombres y rutas canónicas.

## Ejecutar y comprobar

En esta copia ya existe la configuración local. Desde la carpeta del proyecto:

```sh
cd /home/tniia/tania/u/6/mn/paginaweb
.venv/bin/python manage.py check
.venv/bin/python manage.py runserver 127.0.0.1:8765
```

Abrir <http://127.0.0.1:8765/>. El servidor debe permanecer ejecutándose en la terminal.

En otra instalación hay que instalar `requirements.txt` y crear `.env` a partir
de `.env.example`, con una clave propia. Para usar SQLite en desarrollo se necesita
`DEBUG=True`, `NUMLEARN_DEBUG=True`, `ALLOW_SQLITE=True` y `DATABASE_URL` vacío.
Después se ejecuta `python manage.py migrate`. El ejemplo de configuración viene
preparado para PostgreSQL, así que copiarlo sin ajustarlo requiere esa base disponible.

Las comprobaciones habituales son:

```sh
.venv/bin/python manage.py check
.venv/bin/python manage.py makemigrations --check --dry-run
.venv/bin/python manage.py test
npm test
```

Para comprobar el navegador, con dependencias de Node y Google Chrome instalados:

```sh
NUMLEARN_TEST_SERVER=1 npm run test:browser
```

Ese comando inicia y cierra su propio servidor en el puerto 8767.
Si ya hay un servidor en 8765, también se puede usar `npm run test:browser`.

**Resultados confirmados el 22/10/2026:** 63 pruebas Django, comprobación de
sintaxis de JavaScript y 8 escenarios Chrome aprobados. También pasó
[GitHub Actions para la base `675a2c4`](https://github.com/tniia/metodos-numericos/actions/runs/39819207566).
Los escenarios Chrome comprueban cálculos, errores y respuestas antiguas con los
CDN bloqueados; no acreditan por sí solos la apariencia de las gráficas con Plotly cargado.

**Revisión del 29/10/2026:** se comprobó la configuración y el estado de las
migraciones y se incorporaron los dos commits nuevos de GitHub. Sobre `6fe5280`
pasaron **69 pruebas Django**, la comprobación de sintaxis de JavaScript y
**8 escenarios Chrome**. No se detectaron cambios pendientes en los modelos.

**Trabajo local posterior de UX y práctica:** pasaron **92 pruebas Django**, las
comprobaciones de sintaxis y LaTeX en JavaScript y **35 escenarios Chrome**, incluidas
las actividades, corrección por campo y verificaciones básicas de accesibilidad. No requiere migraciones. El commit base es `6fe5280`; la revisión de UX continúa en
`feat/laboratorio-metodos-numericos`. El identificador de esta entrega se consulta
con `git log -1 --oneline`.

## Puntos presentes antes de modificar

- La indicación anterior fue corregir errores conservando las explicaciones,
  las guías y el diseño de la entrega. Los cambios de Andrés ya forman parte de
  la base actual. La retroalimentación posterior motivó los cambios locales
  descritos en `docs/UX_APRENDIZAJE.md`. El diagnóstico original se conserva en
  `REVISION_RETROALIMENTACION.md`.
- En sistemas lineales ya se retiran las respuestas al editar datos y se ignoran
  respuestas tardías de solicitudes anteriores. Esa corrección está en `static/js/linear/lab.js`.
- El residuo mide cuánto se incumplen las ecuaciones; no equivale al error real
  de la solución. Los criterios de convergencia y sus límites forman parte del contenido.
- `README.md` contiene información antigua: menciona archivos de `docs/` que ya
  no están, pruebas retiradas, ejercicios eliminados y que el módulo 2 está pendiente.
  Se corrigió «Acerca de NumLearn» de Recursos para indicar los dos módulos
  disponibles. El README conserva secciones históricas y tiene una nota de estado
  al principio.
- Las tablas de los ejercicios resueltos están escritas en `WORKED_EXAMPLES`;
  los simuladores calculan por separado al ejecutarlos. Modificar una tabla de
  ejemplo no cambia el algoritmo del servicio ni sus valores por defecto.
- La migración `nonlinear.0003_remove_quiz_models` elimina los modelos de ejercicios
  e intentos. Ya está aplicada en la base local. El respaldo anterior permite
  recuperar el estado previo si se necesita consultar ese material.
- Hay configuración para Render, pero subir código a GitHub no equivale a publicar
  una web. En esta conversación no se confirmó un despliegue de producción.

## Archivos de apoyo

En Descargas se recibieron `informe-exposicion-sistemas-lineales.md (1).pdf` y
`numlearn-sistemas-lineales (1).zip`. El PDF explica el módulo lineal y propone
un recorrido de exposición.

En la carpeta local también hay `informes_actualizados/`, archivos ZIP de informes,
las imágenes `1.jpeg` a `6.jpeg` y
`respaldo-antes-del-zip-20261022-115012.tar.gz`. El respaldo contiene los archivos
y la base local anteriores al reemplazo; excluye Git y las dependencias instaladas.
Estos materiales figuran sin seguimiento y no se incluyeron en el último commit.

`.env` y `db.sqlite3` son locales y están ignorados por Git. Este resumen no incluye
sus claves ni datos personales. El commit de referencia y el respaldo permiten
comparar los próximos cambios con el estado desde el que se retoma el proyecto.
