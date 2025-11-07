# 📊 Sistema Distribuido de Reportes Financieros Automatizados

## Descripción del Proyecto

Este proyecto implementa un sistema distribuido para la generación, difusión y consulta de indicadores financieros de criptomonedas. Combina automatización diaria, arquitectura cliente-servidor, comunicación en tiempo real y suscripción por correo.

El sistema permite:

- Generar reportes diarios en Excel, Word y PDF.
- Difundir datos en tiempo real por web
- Enviar correos automáticos a suscriptores.
- Difundir datos por broadcast y multidifusión según la criptomoneda.

---

## Tecnologías Utilizadas

### Backend
- **FastAPI**: servidor principal y API REST.
- **RPC**: comunicación entre nodos para generación de reportes.
  - Librería: `gRPC`
- **Colas de mensajes**: para gestionar peticiones de archivos.
  - RabbitMQ (`pika`) o Kafka (`confluent-kafka`).
- **Correo electrónico**: `smtplib`.

### Frontend
- **React**: interfaz web para visualizar datos y suscribirse por correo.

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
  - Envío automático diario.

- **Documentación**: [Documentación](/docs/doc.md)

---

## Instalación y Ejecución Local

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/User281167/cripto-rpc.git
   cd cripto-rpc
   ```

2. Instalar dependencias:
   ```bash
   # dependencias de desarrollo cada servicio tiene sus dependencias
   pip install -r requirements.txt
   ```

3. Ejecutar de servicios

   ```bash
   docker run -d --name redis-rpc-info -p 6380:6379 redis:7
   python rpc_info/server.py
   python rpc_info/workers.py

   python rpc_report/server.p
   python rpc_email/server.py
   python socket_service/main.py
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

## Servicio Reportes
``` bash
python -m grpc_tools.protoc -I./proto --python_out=./generated --grpc_python_out=./generated ./proto/report.proto

# En el archivo generado en `report_pb2_grpc.py` se debe cambiar la importación
import report_pb2 as report__pb2

# a
from . import report_pb2 as report__pb2

# Ejecutar el servicio en segundo plano
python rpc_report/server.py
```

## Servicio Email
``` bash
python -m grpc_tools.protoc -I./proto --python_out=./generated --grpc_python_out=./generated ./proto/email.proto

# En el archivo generado en `email_pb2_grpc.py` se debe cambiar la importación
import email_pb2 as email__pb2

# a
from . import email_pb2 as email__pb2

# Ejecutar el servicio en segundo plano
python rpc_email/server.py
```

## Servicio de socket

Se encarga de conectar y hacer stream de datos para el frontend
``` bash
python socket_service/main.py

# Crear y levantar contenedor Redis para sockets
docker run -d --name redis-socket-io -p 6381:6379 redis:7
```