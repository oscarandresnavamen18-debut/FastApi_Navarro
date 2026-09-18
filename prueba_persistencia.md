# Prueba de persistencia

## Fecha
17 de septiembre de 2026

## Hora de inicio
11:03

## Hora de reinicio
11:04

## Procedimiento

1. Se verificaron los 4 posts restantes en la base de datos.
2. Se anotó la hora antes de detener el servidor.
3. Se detuvo completamente el servidor con Ctrl+C.
4. Se esperaron unos segundos.
5. Se volvió a iniciar el servidor con Uvicorn.
6. Se anotó la hora de reinicio.
7. Inmediatamente se ejecutó GET /posts desde Swagger.

## Resultado

Después de reiniciar el servidor, GET /posts mostró nuevamente los
4 posts restantes.

Los posts conservaron sus cambios realizados anteriormente mediante
PUT y PATCH y no fue necesario crearlos nuevamente.

Esto confirma que los datos permanecieron guardados en la base de datos
SQLite después de detener y volver a iniciar el servidor.

## Respuesta obtenida

{
  "total": 4,
  "data": [
    ...
  ]
}

## Evidencia

Se adjunta la captura de GET /posts realizada inmediatamente después
de reiniciar el servidor.