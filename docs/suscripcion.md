```mermaid
graph TD
  A[Formulario de suscripción]
  B[Base de datos de correos]
  C[Servicio programado diario]
  D[Nodo RPC de archivos]
  E[Correo con reporte]

  A --> B
  C --> B
  C --> D
  D --> E
```