# NumLearn

**Métodos Numéricos Interactivos** · Laboratorio universitario con Django.

## Menú lateral auto-ocultable y animaciones de teoría

- **Menú lateral**: en escritorio queda oculto por defecto y el contenido usa todo
  el ancho. Aparece al acercar el puntero al borde izquierdo (hay una pestaña como
  pista), al navegar con el teclado o con el botón ☰. El pequeño botón con el
  **dardo** lo fija; la preferencia se guarda en el navegador (`localStorage`) y se
  aplica antes de pintar la página. En móvil se conserva el menú desplegable.
- **«Iniciar animación»**: cada ejercicio resuelto (los seis métodos de raíces,
  eliminación gaussiana y Gauss-Seidel) y los ejemplos de teoría de *Errores
  numéricos*, *Raíces de ecuaciones*, *Raíces de polinomios* y *Formulación* de
  sistemas lineales tienen una animación con dos modos: **Paso a paso** (anterior /
  siguiente, teclas ← →) y **Automático** (reproducir / pausar con velocidad Lenta,
  Normal o Rápida). Los valores se calculan en el navegador con los datos del
  ejemplo y coinciden con las tablas; el paso de la lista y la fila de la tabla se
  resaltan a la vez. La animación de errores usa los datos del explorador.
- Código: `static/js/theory-animation.js`, `static/js/animations/` (motor, dibujo
  SVG y escenas), `static/css/sidebar-dock.css`, `static/css/theory-animation.css`
  y `templates/components/theory_animation.html`. Pruebas: `core/test_interface.py`,
  `tests/theory-animation.test.cjs` y `tests/browser/theory-animation.spec.cjs`.


## UX de aprendizaje — revisión del 29/10/2026

La entrega se centra en **un tema: Errores numéricos**. Portada, teoría,
práctica y autoevaluación siguen ese mismo recorrido. Hay **12 ejercicios**
de errores y un banco de **20 preguntas**; cada evaluación presenta cinco
preguntas de conceptos y después cinco de aplicación. La meta es ocho aciertos.

La lección separa Conceptos y medidas, Origen del error y Explorador. La práctica
incluye escalas distintas, redondeo, truncamiento, referencia cero y tolerancia
inclusiva, con LaTeX y corrección por campo. Los intentos de este tema se guardan
aparte de las actividades generales anteriores.

Los demás temas quedan en **Otros recorridos** y en un catálogo secundario.
Todas las funciones de las calculadoras se conservan. Consulta el
[recorrido, alcance y uso de IA](docs/UX_APRENDIZAJE.md) y el
[fundamento académico de errores](docs/FUNDAMENTO_ERRORES.md).

Rutas principales: `/ecuaciones-no-lineales/errores/`, `/ecuaciones-no-lineales/practica/` y
`/ecuaciones-no-lineales/autoevaluacion/`. Las siguientes secciones del README
conservan referencias de entregas anteriores; algunos enlaces de documentación
y conteos históricos no describen esta revisión.


Aprende a encontrar raíces, analiza errores y observa cómo convergen seis métodos.
El módulo 1 incluye teoría, gráficas, simulación paso a paso, un comparador de recorridos
con propagación de errores y análisis de convergencia/divergencia, búsqueda global.
El módulo 2 (sistemas lineales) está disponible; los otros tres aparecen como «Próximamente». El quiz antiguo se retiró; esta revisión añade práctica guiada y autoevaluación con una nueva validación.
No hace falta registrarse para calcular o practicar. Los accesos personales están
retirados de la navegación en esta revisión; sus datos anteriores se conservan.

El prototipo previo de sistemas lineales sigue intacto en `index.html`, `css/`, `js/`
y `tests/`. Su README original se conserva íntegro en
[docs/PROTOTIPO_EQUIPO_2.md](docs/PROTOTIPO_EQUIPO_2.md).

## Tecnologías y requisitos

- Python 3.12–3.14, Django 5.2 LTS, PostgreSQL y psycopg 3.
- SymPy, django-environ, WhiteNoise y Gunicorn en Linux.
- Django Templates, Bootstrap 5, Bootstrap Icons, JavaScript ES modules,
  Plotly.js y MathJax. Sin React, Vue ni Angular.
- PostgreSQL local o remoto; SQLite solo como fallback explícito de desarrollo.
- Internet para instalar dependencias y cargar bibliotecas frontend desde CDN.
- Git; Node 22+ para pruebas JavaScript y de navegador (sin build obligatorio).

Validado localmente con Python 3.14.6 y Django 5.2.17. Las dependencias tienen rangos
acotados; para un despliegue reproducible, revisar y fijar versiones después de
pasar CI. Gunicorn no se instala en Windows: allí se utiliza runserver.

## Rama de mejoras y validación local

La rama `feat/laboratorio-metodos-numericos` continúa el commit `15d55fe` de
`feature/modulo-ecuaciones-no-lineales`. Consulta la [auditoría](AUDITORIA_PLATAFORMA.md)
y el [plan de mejoras](PLAN_MEJORAS.md). Los informes académicos están fuera del
repositorio, en la carpeta padre `mn`.

En Linux, tras instalar `requirements.txt` en `.venv`, puedes usar SQLite de desarrollo
sin crear ni sobrescribir `.env` (clave de ejemplo solo para pruebas locales):

```sh
export NUMLEARN_DEBUG=True ALLOW_SQLITE=True SECRET_KEY=local-validation-only DATABASE_URL=
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver 127.0.0.1:8765
```

Abre http://127.0.0.1:8765/. Usa las instrucciones generales siguientes para otra
instalación y una clave privada para cualquier entorno compartido.

## Instalación desde otra copia

```sh
git clone https://github.com/tniia/metodos-numericos.git
cd metodos-numericos
git switch feat/laboratorio-metodos-numericos
python -m venv venv
```

Activar en Windows PowerShell: `venv\Scripts\Activate.ps1`.
En CMD: `venv\Scripts\activate.bat`.
En Linux/macOS: `source venv/bin/activate`.

```sh
pip install -r requirements.txt
```

Copiar `.env.example` a `.env`: `Copy-Item .env.example .env` en PowerShell,
o `cp .env.example .env` en Linux/macOS. Genera una clave y pégala en SECRET_KEY:

```sh
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Nunca publiques `.env`, claves ni contraseñas. No sobrescribas el `.env` existente
si ya tiene tu configuración.

## Variables de entorno

| Variable | Desarrollo | Producción |
| --- | --- | --- |
| `SECRET_KEY` | Clave aleatoria local | Clave privada aleatoria de al menos 50 caracteres |
| `DEBUG` | `True` | `False` |
| `NUMLEARN_DEBUG` | `True` si hay conflicto con DEBUG global | `False` o ausente |
| `DATABASE_URL` | URL de PostgreSQL; vacía solo para SQLite | URL de PostgreSQL obligatoria |
| `ALLOW_SQLITE` | `True` solo si se necesita fallback | `False` |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Dominio del servicio sin https |
| `CSRF_TRUSTED_ORIGINS` | Vacía para mismo origen local | `https://tu-servicio.onrender.com` |
| `SECURE_SSL_REDIRECT` | No aplica con DEBUG | `True` |

Las variables del proceso prevalecen sobre `.env`. `NUMLEARN_DEBUG`, si existe,
prevalece sobre DEBUG: en esta máquina había un DEBUG global con el valor `release`.
**En producción ambos deben ser False**. El `.env.example` configura PostgreSQL
como opción oficial. Para el fallback local usa:

```dotenv
DEBUG=True
NUMLEARN_DEBUG=True
ALLOW_SQLITE=True
DATABASE_URL=
```

## PostgreSQL

Instala/inicia PostgreSQL y entra como administrador con `psql -U postgres`.
Crea un usuario y una base exclusivos, eligiendo tu propia contraseña:

```sql
CREATE USER numlearn WITH PASSWORD 'elige-una-clave-privada';
CREATE DATABASE numlearn OWNER numlearn;
```

Configura `.env` con `DATABASE_URL=postgres://numlearn:TU_CLAVE@localhost:5432/numlearn`
y `ALLOW_SQLITE=False`. Codifica caracteres reservados de la contraseña en la URL.
Para conexiones remotas usa las opciones TLS exigidas por tu proveedor, por ejemplo
`?sslmode=require`. Cambiar desde SQLite no traslada automáticamente sus datos.

```sh
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Las migraciones crean tablas y los 12 ejercicios sin ejecutar un comando de carga
adicional. El superusuario es opcional; permite administrar ejercicios en `/admin/`.
Para correr tests con PostgreSQL, el usuario de pruebas necesita permiso CREATEDB
(o una base de pruebas preparada). No concedas ese permiso al usuario de producción.

## Estructura

```text
metodos-numericos/
├── manage.py, requirements.txt, .env.example, .gitignore
├── Procfile, render.yaml
├── config/                 settings, rutas, WSGI y ASGI
├── core/                   dashboard, cuentas, progreso y apuntes
│   └── migrations/
├── nonlinear/
│   ├── catalog.py          registro compartido de métodos y temas
│   ├── forms.py, models.py, views.py, urls.py, api_urls.py
│   ├── services/           parser, errores, algoritmos, gráficas, evaluación
│   ├── migrations/         esquema y carga de ejercicios
│   └── tests/              pruebas de servicios, API, cuentas y persistencia
├── templates/
│   ├── base.html
│   ├── components/         sidebar, navbar, cards, asistente y otros parciales
│   ├── core/, nonlinear/, registration/
├── static/
│   ├── css/app.css
│   ├── js/app.js
│   ├── js/nonlinear/       common, simulator, visualizers, compare, learning, assessment
│   └── icons/favicon.svg
├── docs/                   arquitectura, API, validación y README anterior
├── .github/workflows/      CI con PostgreSQL
└── index.html, css/, js/, tests/    prototipo original conservado
```

Modelos: `UserProgress`, `CalculationHistory` y `StudyNote`. No se han creado modelos
vacíos para los módulos futuros.

Consulta [arquitectura](docs/ARCHITECTURE.md) para ampliar la plataforma y
[API](docs/API.md) para integrar el frontend. La lógica matemática no vive en las vistas.

## Rutas

- `/`: dashboard; `/ecuaciones-no-lineales/`: ruta del módulo 1.
- Dentro de `/ecuaciones-no-lineales/`: `conceptos/`, `errores/`, `polinomios/`, `busqueda/`,
  `biseccion/`, `regla-falsa/`, `punto-fijo/`, `newton/`, `secante/`,
  `raices-multiples/`, `comparar/`. Cada contenido tiene una sola URL
  (ver comentarios en `nonlinear/urls.py`); `laboratorio/` solo redirige (301) a la
  URL canónica del método pedido, para no romper enlaces antiguos.
- Módulo 2 (app `linear`): `/sistemas-lineales/` con `formulacion/`, `eliminacion-gaussiana/`, `gauss-seidel/`,
  y `comparacion-metodos/`; `laboratorio/?method=` redirige (301). API: POST `/api/linear/gauss/`,
  `seidel/`, `compare/` y `progress/`. Los cálculos de usuarios autenticados se guardan en `CalculationHistory`
  con método `linear-gauss`, `linear-seidel` o `linear-compare`.
- `/buscar/?q=`: única búsqueda del portal (temas del módulo 1 y programa del curso).
- `/cuenta/login/`, `/cuenta/registro/`, `/cuenta/logout/` (POST).
- `/mi-progreso/`, `/mis-apuntes/`, `/favoritos/`, `/recursos/`, `/admin/`, `/health/`.
- POST `/api/nonlinear/bisection/`, `newton/`, `false-position/`, `fixed-point/`,
  `secant/`, `multiple-roots/`; auxiliares en la documentación de API.

## Ruta de aprendizaje

La barra lateral ya no lista los once contenidos del módulo 1: muestra una **ruta de seis pasos**
(Errores → Raíces de ecuaciones → Métodos cerrados → Métodos abiertos → Raíces múltiples de
polinomios → Comparar métodos) y la búsqueda gráfica como herramienta. El módulo 2 sigue la misma
idea en cuatro pasos (Formulación → Métodos directos → Métodos iterativos → Comparar). Dentro de
cada simulador un selector agrupado por familia (cerrados/abiertos, directos/iterativos) permite
cambiar de método conservando los datos; todas las URL canónicas, el historial y el progreso se
mantienen. Cada método incluye un **ejercicio resuelto** con valores a seis decimales y un botón
para reproducirlo en el simulador (`ROUTE`, `FAMILIES` y `WORKED_EXAMPLES` en `nonlinear/catalog.py`
y `linear/catalog.py`).

## Uso del laboratorio

Ejecutar muestra todo el cálculo. Siguiente iteración empieza por la primera fila
si todavía no se ejecutó y avanza una a una; Modo automático reproduce la trayectoria
y permite pausarla. Anterior, el selector y los botones de fila permiten regresar
a cualquier paso; sincronizan construcción geométrica, tabla y residuo. El rango X/Y
sólo cambia la vista. Reiniciar restaura el ejemplo inicial. Cambiar parámetros invalida
el cálculo previo. En laboratorio se puede cambiar de método manteniendo la función;
para punto fijo el campo se interpreta como **g(x)** y debes elegir una transformación
adecuada. El selector de ejemplos proporciona transformaciones para ese método.

Los gráficos muestran intervalos, tangentes, secantes o escalera de punto fijo según
corresponda. El comparador verifica el residuo original al usar g(x) y no proclama un
método ganador. El asistente muestra mensajes deterministas; no utiliza IA externa.

## Verificación

```sh
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
node --experimental-vm-modules --test tests/prueba.test.cjs tests/visualizers.test.cjs tests/javascript-syntax.test.cjs
python manage.py collectstatic --noinput
```

El workflow de GitHub Actions repite las pruebas con PostgreSQL 16 y Python 3.12.
Ese workflow se ejecutará al subir la rama: prepararlo no equivale a haberlo ejecutado.
Ver [VALIDATION.md](docs/VALIDATION.md) para resultados locales y límites de verificación.

## Git y colaboración

La base remota auditada está en `feature/modulo-ecuaciones-no-lineales`; las mejoras
locales están en `feat/laboratorio-metodos-numericos`, en commits por bloque.
Antes de integrar, revisa `git status`, `git log` y `git diff`. La rama de mejoras
se publicó en GitHub el 24/09/2026; `main` permanece sin modificaciones. No incluyas `.env`, bases locales, `.venv` o `node_modules`.

Si Git pide autenticación en VS Code: abre la terminal integrada y ejecuta el push;
completa el inicio de sesión de Git Credential Manager en el navegador con una cuenta
que tenga permiso de escritura. Alternativamente, con GitHub CLI instalado ejecuta
`gh auth login`, elige GitHub.com, HTTPS y autenticación por navegador, después
`gh auth setup-git`. No pegues tokens en archivos del proyecto ni en mensajes de commit.

## Despliegue en Render

`render.yaml` define un servicio Python y PostgreSQL. Los planes declarados son de
pago; revisa la selección y el costo en Render antes de crear los recursos.
No se ha creado un servicio ni una base remota desde esta sesión.

1. Sube la rama y autoriza a Render a leer el repositorio.
2. En Render, crea un Blueprint desde esta rama y su `render.yaml`, o crea manualmente
   PostgreSQL y un Web Service Python apuntando al repositorio.
3. La raíz del servicio es la raíz del repositorio (la carpeta que contiene manage.py).
4. Configura `ALLOWED_HOSTS` con el hostname asignado y `CSRF_TRUSTED_ORIGINS` con su URL
   https. El Blueprint genera SECRET_KEY y enlaza DATABASE_URL. DEBUG y NUMLEARN_DEBUG
   deben ser False; ALLOW_SQLITE debe ser False.
5. Build y start:

```sh
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 60
```

6. Revisa los logs, `/health/`, la página de inicio y un cálculo con login y sin login.
   Ejecuta `python manage.py check --deploy` con las variables reales.
7. Crea el administrador en Render Shell: `python manage.py createsuperuser`.

WhiteNoise sirve estáticos con hash y compresión en producción. La configuración
confía en X-Forwarded-Proto solo detrás del proxy de Render/Railway; en otro entorno
ajusta esa confianza según el proxy utilizado. HTTPS, cookies seguras y HSTS se
activan con DEBUG=False. En Railway puedes reutilizar las mismas variables y el
Procfile; conecta su PostgreSQL y configura migrate como paso de despliegue.

Referencias oficiales: [Django 5.2](https://docs.djangoproject.com/en/5.2/releases/5.2/),
[WhiteNoise](https://whitenoise.readthedocs.io/en/stable/django.html),
[Render Django](https://render.com/docs/deploy-django),
[Render Blueprint](https://render.com/docs/blueprint-spec).

## Alcance y revisión manual

No se implementaron algoritmos de los módulos 2–5, pagos, chat IA ni aplicación móvil.
No se adjuntaron los mockups mencionados; la interfaz sigue la especificación textual.
Las mejoras se verificaron con Chrome en escritorio y móvil; otras plataformas y
el flujo completo de cuentas requieren revisión adicional.
PostgreSQL remoto y despliegue real requieren la configuración manual indicada arriba.
Los simuladores no prueban automáticamente continuidad y una gráfica muestreada puede
omitir raíces o discontinuidades; estos límites aparecen también en la interfaz.

## Pruebas de las mejoras

Con las variables de desarrollo anteriores:

```sh
.venv/bin/python manage.py test
npm ci
npm test
```

Con el servidor en `127.0.0.1:8765` y Google Chrome instalado:

```sh
npm run test:browser
```

`NUMLEARN_TEST_URL` permite elegir otra URL de **pruebas**. Playwright usa el canal
Chrome instalado; no se descargan navegadores durante `npm ci`. Las pruebas envían
cálculos como invitado y no deben apuntarse a un entorno de producción. Evidencias
regenerables y trazas de fallos quedan en `test-results/` (ignorado).

Resultado del 24/09/2026 tras integrar la revisión 2: 84 pruebas Django,
cinco archivos de pruebas JS y 32
escenarios Chrome. Se comprueban simuladores, capítulos de
portada, fórmulas dinámicas, teclado, contraste, resultados obsoletos y fallbacks.
La búsqueda gráfica separa ceros muestreados de cambios de signo y permite
llevar un intervalo candidato al laboratorio; se prueban polos, entradas
inválidas y respuestas tardías al modificar los datos.
Se conservan las regresiones móviles existentes. Capturas y alcance
de accesibilidad en la auditoría.
En navegador aprobaron 25 escenarios inicialmente y los siete restantes al
repetir los fallos de conexión y ajustar la simulación de recursos ausentes a SRI.
Se verifican además el CSV, los enlaces con límite de iteraciones y la recuperación
de contraseña. El envío de correo real requiere configurar `EMAIL_URL`.


## Diseño y fuentes locales

La interfaz mantiene azul marino y violeta, con IBM Plex Sans y Mono servidas por
Django. Se reorganizaron portada, navegación y acceso/registro conservando los
simuladores. Consulta [decisiones, fuentes UX y validación](docs/DISENO_Y_FUENTES.md).
Las tipografías WOFF2 y sus licencias están versionadas; `npm run fonts:sync` permite
regenerarlas después de `npm ci`. No hay descarga de Google Fonts al abrir la página.

## Revisión 2 — mejoras de interfaz, cuentas y robustez

Se conserva la portada por capítulos, los desplegables personalizados y las
lecciones de errores, ecuaciones y polinomios. Las decisiones de esa interfaz
están en [interfaz de los tres temas](docs/INTERFAZ_TRES_TEMAS.md).

Tabla de iteraciones a ancho completo, encuadre automático de la gráfica, fórmula de
cada paso con valores sustituidos, exportación CSV y enlaces compartibles en el
simulador. Registro con correo y recuperación de contraseña (`/cuenta/recuperar/`),
borrado de apuntes e historial, «Mi progreso» con temas y aciertos, adopción del
progreso de invitado al iniciar sesión, límite de peticiones a la API, `LOGGING` y SRI
en los recursos CDN. Detalle, archivos y verificación en
[docs/MEJORAS_REVISION_2.md](docs/MEJORAS_REVISION_2.md). Variables opcionales:
`EMAIL_URL`, `DEFAULT_FROM_EMAIL`, `NUMLEARN_API_RATE_LIMIT` (ver `.env.example`).
