```mermaid
graph TD
  A[Cliente Web]
  B[Bot de Telegram]
  C[Servidor FastAPI]
  D[Cola de peticiones]
  E[Nodo RPC - Info]
  F[Nodo RPC - Archivos]
  G[Cache]
  H[Reportes]
  I[Correo]
  J[BD Suscriptores]
  K[Servicio diario]

  A --> C
  B --> C
  C --> D
  C --> E
  C --> F
  E --> G
  F --> H
  H --> I
  J --> K
  K --> F
  K --> I
```