# 📊 Sistema Distribuido de Reportes Financieros Automatizados

## Descripción del Proyecto

Este proyecto implementa un sistema distribuido para la generación, difusión y consulta de indicadores financieros clave (como dólar, euro, bitcoin, petróleo e índices bursátiles). Combina automatización diaria, arquitectura cliente-servidor, comunicación en tiempo real y suscripción por correo.

El sistema permite:

- Generar reportes diarios en Excel, Word y PDF.
- Difundir datos en tiempo real por web y Telegram.
- Enviar correos automáticos a suscriptores.
- Consultar indicadores vía comandos en Telegram.
- Difundir datos por broadcast y multidifusión según la criptomoneda.

---

## Tecnologías Utilizadas

### Backend
- **FastAPI**: servidor principal y API REST.
- **RPC**: comunicación entre nodos para generación de reportes.
  - Librería: `gRPC`
- **Colas de mensajes**: para gestionar peticiones de archivos.
  - RabbitMQ (`pika`) o Kafka (`confluent-kafka`).
- **Programación de tareas**: `cron` (Linux) o `APScheduler` (Python).
- **Correo electrónico**: `smtplib`, `email`, o servicios como SendGrid.

### Frontend
- **React**: interfaz web para visualizar datos y suscribirse por correo.

### Bot de Telegram
- `python-telegram-bot` o `telebot` para comandos como `/dolar`, `/bitcoin`, `/reporte`.

### Reportes
- **Excel**: `openpyxl` o `pandas`.
- **Word**: `python-docx`.
- **PDF**: `reportlab` o `fpdf`.

### Base de Datos
- SQLite, PostgreSQL o MongoDB para almacenar suscriptores.

---

## Funcionalidades

- **Difusión de datos**:
  - Broadcast: resumen de las 5 criptomonedas más relevantes.
  - Multicast: datos específicos por moneda.
- **Generación de reportes**:
  - Datos crudos + análisis de variación porcentual.
  - Archivos Excel, Word y PDF.
- **Suscripción por correo**:
  - Endpoint para registrar correos.
  - Envío automático diario a las 00:00.
- **Bot de Telegram**:
  - Comandos para consultar cotizaciones en tiempo real.
  - Envío del último reporte PDF.

---

## Diagramas de Arquitectura

Los siguientes diagramas están escritos en formato Mermaid y pueden visualizarse directamente en GitHub si se usa una extensión como [Mermaid Markdown Viewer](https://github.com/BackMarket/github-mermaid-extension)

## Diagramas del Sistema

- [Diagrama de Componentes](/docs/diagrama-componentes.md)
- [Flujo de Datos](/docs/flujo-datos.md)
- [Difusión de Datos](/docs/difusion.md)
- [Suscripción por Correo](/docs/suscripcion.md)



---

## Instalación y Ejecución Local

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/User281167/cripto-rpc.git
   cd cripto-rpc
   ```

2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Ejecutar el servidor FastAPI:
   ```bash
   uvicorn main:app --reload
   ```

4. Servicio Crypto info:
   ```bash
   python rpc_info/server.py
   ```
---

# Compilación de Archivos .proto para Servicios gRPC y Ejecución local
## Servicio Crypto
``` bash
python -m grpc_tools.protoc -I./proto --python_out=./generated --grpc_python_out=./generated ./proto/crypto.proto

# En el archivo generado en `crypto_pb2_grpc.py` se debe cambiar la importación
import crypto_pb2 as crypto__pb2

# a
from . import crypto_pb2 as crypto__pb2

#levantar instancia de redis
docker run -d --name redis-rpc-info -p 6380:6379 redis:7
docker start redis-rpc-info


# Ejecutar workers en segundo plano
python rpc_info/workers.py

# Ejecutar el servicio en segundo plano
python rpc_info/server.py
```