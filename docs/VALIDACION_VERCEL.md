# Revisión del 11 de noviembre de 2026

## Resultado local

- 174 pruebas Django aprobadas con PostgreSQL en una base aislada.
- Los cuatro archivos de pruebas JavaScript aprobaron `npm test`.
- 41 escenarios Chrome aprobados: móvil, menú, teclado, accesibilidad básica,
  práctica, autoevaluación, seis métodos de raíces, sistemas lineales,
  comparación, exportación y animaciones.
- 14 páginas comprobadas con configuración de producción, HTTPS y estáticos
  con manifest. Registro, acceso y recuperación muestran sus formularios.
- Se iniciaron práctica y autoevaluación con comprobación CSRF real. Sus sesiones
  se conservaron después de cerrar la conexión PostgreSQL y usar otro cliente
  con las mismas cookies. Un origen ajeno recibió HTTP 403.
- El build de producción pasó `check --deploy` sin avisos, creó el esquema
  PostgreSQL desde cero y volvió a ejecutarse sin migraciones pendientes.
- `collectstatic` terminó correctamente en producción y no hay cambios de
  modelos pendientes de migración.

## Cambios para el despliegue

Se versionan `vercel.json`, `.vercelignore` y la versión de Python. Se detectan
los dominios de Vercel, se desactiva DEBUG y se admiten `DATABASE_URL` o
`POSTGRES_URL`. El build aplica migraciones con un bloqueo de transacción
compatible con conexiones agrupadas. CI incluye la comprobación del build.

## Límites

Estas comprobaciones son locales; no equivalen a un despliegue remoto exitoso
ni a una ejecución de GitHub Actions. No hay una conexión de Vercel autorizada
ni credenciales PostgreSQL remotas disponibles en esta sesión. La publicación
depende de autorizar esa conexión y configurar los secretos del proyecto.

El envío real de correo necesita `EMAIL_URL` de un proveedor SMTP. La revisión
del navegador usa Chrome, incluida emulación móvil; no certifica todos los
navegadores o dispositivos físicos. Véase [VERCEL.md](VERCEL.md).
