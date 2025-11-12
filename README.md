# 📊 Sistema Distribuido de Reportes Financieros de Criptomonedas

Sistema distribuido de microservicios para obtener información de criptomonedas en tiempo real, generar reportes automatizados y proporcionar una interfaz web interactiva.

## 🏗️ Arquitectura

El sistema está compuesto por:

- **Servicios RPC (gRPC)**:
  - `rpc_info`: Obtiene y cachea datos de criptomonedas desde CoinGecko
  - `rpc_report`: Genera reportes en Excel, Word, PDF y PNG
  - `rpc_email`: Gestiona suscripciones y envío de correos automáticos

- **API Gateway (FastAPI)**: Punto de entrada REST para todos los servicios
- **Socket Service**: WebSocket para actualizaciones en tiempo real
- **Cliente Web (React + TypeScript)**: Interfaz de usuario moderna

## 🚀 Inicio Rápido

### Requisitos Previos

- Python 3.8+
- Node.js 18+
- Docker Desktop
- Git

### Instalación

1. **Clonar el repositorio**:
```bash
git clone https://github.com/User281167/cripto-rpc.git
cd cripto-rpc
```

2. **Instalar dependencias de Python**:
```bash
pip install -r requirements.txt
```

3. **Compilar Protocol Buffers**:
```bash
# Windows
compile_proto.bat

# Linux/Mac
python -m grpc_tools.protoc -I./proto --python_out=./generated --grpc_python_out=./generated ./proto/crypto.proto
python -m grpc_tools.protoc -I./proto --python_out=./generated --grpc_python_out=./generated ./proto/report.proto
python -m grpc_tools.protoc -I./proto --python_out=./generated --grpc_python_out=./generated ./proto/email.proto
```

4. **Instalar dependencias del cliente**:
```bash
cd client
npm install
cd ..
```

### Ejecución

**Windows**:
```bash
start_services.bat
```

**Linux/Mac**:
```bash
# Iniciar Redis
docker run -d --name redis-rpc-info -p 6380:6379 redis:7
docker run -d --name redis-socket-io -p 6381:6379 redis:7

# Iniciar servicios (en terminales separadas)
python rpc_info/workers.py
python rpc_info/server.py
python rpc_report/server.py
python rpc_email/server.py
python socket_service/main.py
python api_gateway/main.py

# Iniciar cliente web
cd client
npm run dev
```

### Servicios y Puertos

- **API Gateway**: http://127.0.0.1:8000
- **Socket Service**: http://127.0.0.1:8001
- **RPC Info**: 127.0.0.1:50051
- **RPC Report**: 127.0.0.1:50052
- **RPC Email**: 127.0.0.1:50053
- **Cliente Web**: http://localhost:5173
- **Redis (rpc_info)**: localhost:6380
- **Redis (socket_service)**: localhost:6381

## 📖 Uso

### API REST

#### Health Check
```bash
curl http://127.0.0.1:8000/health
```

#### Generar Reportes
```bash
# Reporte Excel
curl http://127.0.0.1:8000/api/reports/crypto?currency=usd -o reporte.xlsx

# Reporte PDF Ejecutivo
curl http://127.0.0.1:8000/api/reports/executive?currency=usd -o reporte.pdf

# Reporte Word de Tendencias
curl http://127.0.0.1:8000/api/reports/trend?currency=usd -o reporte.docx

# Gráfico PNG
curl http://127.0.0.1:8000/api/reports/graph?currency=usd -o grafico.png
```

#### Suscripciones de Email
```bash
# Suscribirse
curl -X POST http://127.0.0.1:8000/api/subscriptions \
  -H "Content-Type: application/json" \
  -d '{"email": "usuario@example.com", "hour": 9, "minute": 0}'

# Cancelar suscripción
curl -X DELETE http://127.0.0.1:8000/api/subscriptions \
  -H "Content-Type: application/json" \
  -d '{"email": "usuario@example.com"}'
```

### Cliente Web

Abre http://localhost:5173 en tu navegador para:
- Ver las top 50 criptomonedas en tiempo real
- Visualizar gráficos de historial de precios
- Navegar entre diferentes criptomonedas

### Ejemplos Python

Ver la carpeta `examples/` para scripts de ejemplo:
- `get_cryptos.py`: Obtener top criptomonedas
- `get_bitcoin.py`: Obtener información de Bitcoin
- `get_history.py`: Obtener historial de precios
- `report_excel.py`: Generar reporte Excel
- `report_pdf.py`: Generar reporte PDF

## ⚙️ Configuración

Crea un archivo `.env` en la raíz del proyecto para personalizar la configuración:

```env
# Servicios RPC
RPC_INFO=127.0.0.1:50051
RPC_REPORT=127.0.0.1:50052
RPC_EMAIL=127.0.0.1:50053

# Redis
RPC_INFO_REDIS_HOST=127.0.0.1
RPC_INFO_REDIS_PORT=6380
SOCKET_REDIS_URL=redis://localhost:6381

# API Gateway
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000

# Socket Service
SOCKET_BACKEND_HOST=127.0.0.1
SOCKET_BACKEND_PORT=8001

# Email (opcional)
RPC_EMAIL_STMP_SERVER=smtp.gmail.com
RPC_EMAIL_STMP_PORT=587
RPC_EMAIL_USER=tu_email@gmail.com
RPC_EMAIL_PASSWORD=tu_contraseña_app
```

Para el cliente web, crea `client/.env.local`:
```env
VITE_SOCKET_URL=http://127.0.0.1:8001
```

## 🛠️ Tecnologías

### Backend
- **Python 3.8+**
- **gRPC**: Comunicación entre microservicios
- **FastAPI**: API REST y WebSocket
- **Redis**: Caché y pub/sub
- **Docker**: Contenedores para Redis

### Frontend
- **React 18**
- **TypeScript**
- **Vite**: Build tool
- **Tailwind CSS**: Estilos
- **Recharts**: Gráficos
- **Socket.IO**: WebSocket client

### Librerías Python
- `grpcio`, `grpcio-tools`: gRPC
- `fastapi`, `uvicorn`: API web
- `redis`, `aioredis`: Redis client
- `pandas`, `openpyxl`: Procesamiento de datos y Excel
- `python-docx`, `fpdf2`: Generación de documentos
- `matplotlib`: Gráficos
- `socketio`: WebSocket server

## 📁 Estructura del Proyecto

```
cripto-rpc/
├── api_gateway/          # API Gateway REST
├── client/               # Cliente web React
├── generated/            # Código generado de Protocol Buffers
├── models/              # Modelos de datos
├── proto/               # Definiciones Protocol Buffers
├── rpc_email/          # Servicio RPC de emails
├── rpc_info/            # Servicio RPC de información
├── rpc_report/          # Servicio RPC de reportes
├── socket_service/      # Servicio WebSocket
├── utils/               # Utilidades y clientes RPC
├── examples/            # Ejemplos de uso
├── docs/                # Documentación
└── nginx/               # Configuración Nginx (opcional)
```

## 🐛 Solución de Problemas

### Error: "grpcio-tools no está instalado"
```bash
pip install grpcio-tools==1.76.0
```

### Error: "Puerto ya en uso"
Verifica qué proceso usa el puerto:
```bash
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000
```

### Error: "Redis connection failed"
Verifica que los contenedores Docker estén corriendo:
```bash
docker ps
```

### La gráfica no aparece en tiempo real
1. Verifica que el Socket Service esté corriendo (puerto 8001)
2. Revisa la consola del navegador (F12) para errores
3. Verifica que `client/.env.local` tenga `VITE_SOCKET_URL=http://127.0.0.1:8001`

## 📚 Documentación Adicional

- [Documentación de la API](http://127.0.0.1:8000/docs) - Swagger UI interactivo
- [Documentación técnica](docs/doc.md) - Detalles técnicos del sistema

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT.

## 👤 Autor

**User281167**

- GitHub: [@User281167](https://github.com/User281167)
- Repositorio: [cripto-rpc](https://github.com/User281167/cripto-rpc)

## 🙏 Agradecimientos

- CoinGecko API por proporcionar datos de criptomonedas
- Comunidad de código abierto

