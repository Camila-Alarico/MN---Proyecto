# Publicar NumLearn en Vercel

`main` contiene la aplicación Django. El `index.html` de la raíz corresponde al
prototipo anterior y no es la página que debe publicarse.

## Configuración inicial

1. En [Vercel](https://vercel.com/new), importa `tniia/metodos-numericos`.
2. Usa **Framework Preset: Django**, **Root Directory: .** y rama de
   producción **main**. Deja Build Command, Install Command y Output Directory
   sin overrides del panel: el repositorio ya incluye `vercel.json`.
3. En **Storage / Marketplace**, conecta una base **Neon PostgreSQL** al
   proyecto y al entorno **Production**. Si todavía no puedes conectar Storage,
   crea primero el proyecto; el primer build fallará hasta configurar la base.
4. En **Settings → Environment Variables**, añade `SECRET_KEY` y `DATABASE_URL`
   para **Production**, según la tabla siguiente. Si Neon ya añadió
   `POSTGRES_URL`, no hace falta duplicarla como `DATABASE_URL`.
5. Activa **Automatically expose System Environment Variables** en la
   configuración de variables del proyecto para admitir su dominio de Vercel.
6. En **Deployments**, ejecuta **Redeploy** después de guardar las variables.
   Abre el dominio del proyecto cuando el despliegue indique **Ready**.

Para generar el valor de `SECRET_KEY` en tu terminal:

```sh
python3 -c 'import secrets; print(secrets.token_urlsafe(64))'
```

Copia el resultado únicamente al campo de Vercel y conserva la misma clave
entre despliegues. `DATABASE_URL` debe ser la conexión PostgreSQL remota de Neon
(preferiblemente la conexión con pool), con `sslmode=require`; no uses la base
SQLite ni la dirección `localhost` de tu computadora.

Conecta el repositorio `tniia/metodos-numericos`, rama de producción `main`,
con la raíz del repositorio como Root Directory. `vercel.json` selecciona Django,
elimina la carpeta de salida estática y ejecuta `scripts/build_vercel.py`.
`.python-version` fija Python 3.12. Vercel instala `requirements.txt`, descubre
`manage.py` y recopila los estáticos para servirlos desde su CDN.

El proyecto necesita dos secretos de producción, configurados una sola vez:

| Variable | Valor |
| --- | --- |
| `SECRET_KEY` | Una clave aleatoria privada de al menos 50 caracteres. Debe mantenerse entre despliegues. |
| `DATABASE_URL` | Conexión a PostgreSQL remoto, por ejemplo la proporcionada al conectar Neon desde Storage/Marketplace. |

También se acepta `POSTGRES_URL` cuando una integración usa ese nombre y no hay
`DATABASE_URL`. Conecta una base separada para Preview si vas a usar ese entorno;
las migraciones se ejecutan sobre la base configurada para cada despliegue.
No se puede utilizar PostgreSQL de `localhost` ni el SQLite de la computadora.

Con **Automatically expose System Environment Variables** activado en Vercel,
los dominios `VERCEL_URL`, `VERCEL_PROJECT_PRODUCTION_URL` y `VERCEL_BRANCH_URL`
se admiten automáticamente en Django y CSRF. Para otro dominio que no figure en
esas variables, añade `ALLOWED_HOSTS=tu-dominio.com` y
`CSRF_TRUSTED_ORIGINS=https://tu-dominio.com`.

`DEBUG` siempre queda desactivado en Vercel, incluso si se copiaron variables de
desarrollo. Las conexiones PostgreSQL usan TLS por defecto y admiten poolers de
transacciones. Las sesiones y los intentos se guardan en PostgreSQL, no en el
disco temporal de una función.

## Después de la configuración inicial

Cada push a `main` ejecuta las comprobaciones de producción y las migraciones.
Un bloqueo de transacción impide que dos builds migren simultáneamente la misma
base. Las migraciones actuales son transaccionales; una futura migración con
operaciones que exijan `atomic = False` debe adaptar este proceso.
No hace falta ejecutar comandos en la laptop ni mantener un túnel abierto.

Si faltan secretos o la conexión remota falla, el build se detiene. No se
genera una clave aleatoria en cada función ni se activa SQLite como reemplazo.

## Verificación

Abre `/`, `/ecuaciones-no-lineales/practica/` y
`/ecuaciones-no-lineales/autoevaluacion/`. En móvil, abre el menú, cambia de página
y ciérralo. Inicia una práctica y una evaluación, responde y recarga la página;
el avance debe conservarse al consultar teoría o cambiar de pestaña. El botón
de reinicio permite comenzar de nuevo explícitamente.

Los correos de recuperación requieren un proveedor SMTP en `EMAIL_URL`. El
transporte de consola predeterminado no entrega correo a direcciones reales.

## Referencias

- [Django en Vercel](https://vercel.com/docs/frameworks/full-stack/django)
- [Variables del sistema](https://vercel.com/docs/environment-variables/system-environment-variables)
- [Runtime de Python](https://vercel.com/docs/functions/runtimes/python)
