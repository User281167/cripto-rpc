## 1. **Entrada del sistema**

```mermaid
flowchart TD
    A["Cliente Web"] --> n1["Nginx:80"]
    n1 --> n2["FastApi:8000 (REST)"] & n3["SocketIO:8001 (WebSocket)"]
```

- **Cliente Web**: El navegador del usuario que consume la aplicación.
- **Nginx:80**: Proxy inverso que enruta las peticiones HTTP y WebSocket.
- **FastAPI (REST)**: API principal que maneja peticiones HTTP.
- **SocketIO (WebSocket)**: Canal en tiempo real para actualizaciones de precios u otros eventos.

> Este bloque permite que el cliente se conecte a un solo punto (`Nginx`) y reciba tanto datos REST como eventos en tiempo real.

---

## 2. **Servicios RPC y procesamiento**

```mermaid
flowchart TD
    A["SocketIO:8001 (WebSocket)"]
    A --> E["RPC - Info"]
    n13["FastApi:8000 (REST)"] --> n15["Cola de informes"] & n16["RCP - Correo"] & n17["RPC - Archivos"] & n18["RPC - Info"]
    n19["Servicio Informes"] --> n20["RPC - Info"]
    n21["Servicio Info"] --> n22["API coingecko"] & n23["Cache"]
```

- **RPC - Info**: Servicio que consulta datos de criptomonedas (API coingecko).
- **RPC - Archivos**: Servicio que gestiona archivos generados (PDF, EXCEL, WORD, PNG).
- **RPC - Correo**: Servicio que prepara informes y los envía por email.
- **Cola de informes**: Sistema de tareas en background para generar reportes.
- **Servicio Informes**: Encargado de procesar solicitudes de informes.
- **Servicio Info**: Encargado de obtener datos externos (usando la API de CoinGecko) y almacenarlos en caché.

> Este bloque representa la lógica de negocio distribuida, donde cada servicio tiene una responsabilidad clara y se comunica por RPC.

---

## 3. **Servicio de correo**

```mermaid
flowchart TD
    n10["Servicio Correo"] -- Obtener reportes --> n8["RPC - Informes"]
    n10 --> n11["Enviar Correo"] & n12["Suscriptores"]
```

- **Servicio Correo**: Orquestador que solicita reportes y los envía por email.
- **RPC - Informes**: Punto de acceso para obtener reportes generados.
- **Enviar Correo**: Módulo que realiza el envío real.
- **Suscriptores**: Base de datos o lista de destinatarios.

> Este bloque automatiza la distribución de reportes a usuarios suscritos.

---

## Diagrama de difusión

```mermaid
flowchart TD
    A["RPC - Info"] --> B["SocketConnection.stream_and_broadcast"]
    B --> C["Emitir top5_update (broadcast a todos)"]
    B --> D["Emitir top50_update (solo sala top50_subscribers)"]
    E["Cliente Web"] --> F["Socket.IO"]
    F --> G["Sala top50_subscribers"]
    F --> H["Sala específica por crypto_id"]
    I["SocketConnection.poll_crypto_rooms"] --> H
    I --> J["Emitir crypto_update (historial por sala)"]
```

---

### 1. **stream_and_broadcast**
- Se conecta al stream RPC (`Info`) que envía actualizaciones periódicas del top 50.
- Emite dos eventos:
  - `top5_update`: se envía a **todos los clientes conectados**.
  - `top50_update`: se envía **solo a los clientes en la sala `top50_subscribers`**.
- Actualiza el caché local (`cached_top5`, `cached_top50`) para respuestas rápidas.

### 2. **Salas específicas (`join_room`)**
- Los clientes pueden unirse a una sala por `crypto_id` para recibir actualizaciones específicas.
- Cuando hay usuarios activos en una sala, el método `poll_crypto_rooms` consulta el historial de precios y emite `crypto_update` a esa sala.

### 3. **Redis opcional**
- Si se configura `redis_url`, se usa `AsyncRedisManager` para compartir estado entre múltiples instancias del servidor.
- Esto permite escalar horizontalmente sin perder sincronización de eventos.

---


## Diagrama de secuencia: Estrategia de generación de reportes

```mermaid
sequenceDiagram
  participant Cliente
  participant RPC_Report
  participant HashGen
  participant PathResolver
  participant FileSystem
  participant DataFrame
  participant ReportGen

  Cliente->>RPC_Report: create_and_get_crypto_report(data, currency)
  RPC_Report->>HashGen: generate_report_hash(currency, timestamp)
  HashGen-->>RPC_Report: report_hash

  RPC_Report->>PathResolver: get_cached_report_path(report_hash)
  PathResolver-->>RPC_Report: filepath

  RPC_Report->>FileSystem: os.path.exists(filepath)
  alt Reporte existe
    FileSystem-->>RPC_Report: True
    RPC_Report->>FileSystem: open(filepath, "rb")
    FileSystem-->>RPC_Report: content
  else Reporte no existe
    FileSystem-->>RPC_Report: False
    RPC_Report->>DataFrame: crypto_data_to_df(data)
    DataFrame-->>RPC_Report: df
    RPC_Report->>ReportGen: generate_crypto_report(data, df, filepath)
    ReportGen-->>RPC_Report: archivo generado
    RPC_Report->>FileSystem: open(filepath, "rb")
    FileSystem-->>RPC_Report: content
  end

  RPC_Report-->>Cliente: filepath, content
```

---

- El flujo completo desde que el cliente solicita un reporte.
- Cómo se genera un hash único para identificar el reporte.
- Cómo se determina la ruta en caché.
- La bifurcación entre reutilizar un archivo existente o generar uno nuevo.
- La conversión de datos a `DataFrame` y la escritura del archivo.
- La lectura final del archivo para devolverlo al cliente.

---

- **Evita duplicación**: El hash asegura que no se generen reportes repetidos.
- **Optimiza recursos**: Reutiliza archivos si ya existen.
- **Modularidad**: Cada función tiene una responsabilidad clara y puede ser testeada por separado.
- **Escalable**: Puede extenderse fácilmente para otros formatos (PDF, Word, etc.) siguiendo el mismo patrón.

---

## Diagrama de secuencia: Generación y envío de reportes

```mermaid
sequenceDiagram
  participant Cron
  participant EmailCollector
  participant EmailQueue
  participant EmailWorker
  participant RpcInfo
  participant RpcReport
  participant FileSystem
  participant EmailService

  Cron->>EmailCollector: Ejecuta cada minuto
  EmailCollector->>EmailQueue: Pone emails en cola

  loop procesamiento continuo
    EmailWorker->>EmailQueue: Espera tarea
    EmailQueue-->>EmailWorker: Entrega emails
    EmailWorker->>RpcInfo: get_top_cryptos()
    EmailWorker->>RpcReport: generate_bar_graph()
    EmailWorker->>RpcReport: generate_crypto_report()
    EmailWorker->>RpcReport: generate_trend_report()
    EmailWorker->>RpcReport: generate_executive_report()
    RpcInfo-->>EmailWorker: Datos de criptos
    RpcReport-->>EmailWorker: Archivos generados

    EmailWorker->>FileSystem: Guarda archivos temporales
    EmailWorker->>EmailService: Envía correo con adjuntos
    EmailService-->>Usuarios: Reciben correo

    EmailWorker->>FileSystem: Elimina archivos temporales
  end
```

---

- El ciclo completo desde que el **cron** dispara el colector.
- Cómo se **filtran y encolan** los correos.
- El procesamiento asíncrono con múltiples llamadas RPC en paralelo.
- La **generación de archivos**, su almacenamiento temporal y envío.
- La limpieza final del sistema.

---
