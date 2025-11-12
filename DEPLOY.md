# 🚀 Guía de Despliegue

Esta guía detalla cómo desplegar el sistema de reportes financieros de criptomonedas en diferentes entornos.

## 📋 Tabla de Contenidos

- [Requisitos del Sistema](#requisitos-del-sistema)
- [Despliegue Local](#despliegue-local)
- [Despliegue en Producción](#despliegue-en-producción)
- [Despliegue con Docker Compose](#despliegue-con-docker-compose)
- [Despliegue en la Nube](#despliegue-en-la-nube)
- [Configuración de Nginx](#configuración-de-nginx)
- [Monitoreo y Logs](#monitoreo-y-logs)

## Requisitos del Sistema

### Mínimos
- **CPU**: 2 cores
- **RAM**: 4 GB
- **Disco**: 10 GB libres
- **Red**: Conexión a Internet estable

### Recomendados (Producción)
- **CPU**: 4+ cores
- **RAM**: 8+ GB
- **Disco**: 50+ GB (SSD recomendado)
- **Red**: 100+ Mbps

### Software
- Python 3.8+
- Node.js 18+
- Docker 20.10+
- Git

## Despliegue Local

### Paso 1: Clonar y Preparar

```bash
git clone https://github.com/User281167/cripto-rpc.git
cd cripto-rpc
```

### Paso 2: Configurar Entorno Virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### Paso 3: Compilar Protocol Buffers

```bash
# Windows
compile_proto.bat

# Linux/Mac
python -m grpc_tools.protoc -I./proto --python_out=./generated --grpc_python_out=./generated ./proto/crypto.proto
python -m grpc_tools.protoc -I./proto --python_out=./generated --grpc_python_out=./generated ./proto/report.proto
python -m grpc_tools.protoc -I./proto --python_out=./generated --grpc_python_out=./generated ./proto/email.proto
```

### Paso 4: Configurar Variables de Entorno

Crea un archivo `.env` en la raíz:

```env
RPC_INFO=127.0.0.1:50051
RPC_REPORT=127.0.0.1:50052
RPC_EMAIL=127.0.0.1:50053
RPC_INFO_REDIS_HOST=127.0.0.1
RPC_INFO_REDIS_PORT=6380
SOCKET_REDIS_URL=redis://localhost:6381
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
SOCKET_BACKEND_HOST=127.0.0.1
SOCKET_BACKEND_PORT=8001
```

### Paso 5: Iniciar Servicios

**Windows**:
```bash
start_services.bat
```

**Linux/Mac**:
```bash
# Iniciar Redis
docker run -d --name redis-rpc-info -p 6380:6379 redis:7
docker run -d --name redis-socket-io -p 6381:6379 redis:7

# Iniciar servicios en background
nohup python rpc_info/workers.py > logs/rpc_info_workers.log 2>&1 &
nohup python rpc_info/server.py > logs/rpc_info_server.log 2>&1 &
nohup python rpc_report/server.py > logs/rpc_report_server.log 2>&1 &
nohup python rpc_email/server.py > logs/rpc_email_server.log 2>&1 &
nohup python socket_service/main.py > logs/socket_service.log 2>&1 &
nohup python api_gateway/main.py > logs/api_gateway.log 2>&1 &
```

### Paso 6: Iniciar Cliente Web

```bash
cd client
npm install
npm run dev
```

## Despliegue en Producción

### 1. Configurar Servidor

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install -y python3.10 python3-pip nodejs npm docker.io docker-compose git
```

### 2. Configurar Firewall

```bash
# Permitir puertos necesarios
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 8000/tcp  # API Gateway
sudo ufw allow 8001/tcp  # Socket Service
sudo ufw enable
```

### 3. Configurar Servicios como Systemd

Crea archivos de servicio en `/etc/systemd/system/`:

**`/etc/systemd/system/rpc-info.service`**:
```ini
[Unit]
Description=RPC Info Service
After=network.target redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/cripto-rpc
Environment="PATH=/opt/cripto-rpc/venv/bin"
ExecStart=/opt/cripto-rpc/venv/bin/python rpc_info/server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Repite para cada servicio (`rpc-report.service`, `rpc-email.service`, `socket-service.service`, `api-gateway.service`).

**Activar servicios**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable rpc-info rpc-report rpc-email socket-service api-gateway
sudo systemctl start rpc-info rpc-report rpc-email socket-service api-gateway
```

### 4. Configurar Nginx

Ver sección [Configuración de Nginx](#configuración-de-nginx).

## Despliegue con Docker Compose

Crea un archivo `docker-compose.yml`:

```yaml
version: '3.8'

services:
  redis-rpc-info:
    image: redis:7
    ports:
      - "6380:6379"
    volumes:
      - redis-rpc-info-data:/data

  redis-socket-io:
    image: redis:7
    ports:
      - "6381:6379"
    volumes:
      - redis-socket-io-data:/data

  rpc-info-workers:
    build: .
    command: python rpc_info/workers.py
    depends_on:
      - redis-rpc-info
    environment:
      - RPC_INFO_REDIS_HOST=redis-rpc-info
      - RPC_INFO_REDIS_PORT=6379

  rpc-info-server:
    build: .
    command: python rpc_info/server.py
    ports:
      - "50051:50051"
    depends_on:
      - redis-rpc-info
      - rpc-info-workers

  rpc-report-server:
    build: .
    command: python rpc_report/server.py
    ports:
      - "50052:50052"
    depends_on:
      - rpc-info-server

  rpc-email-server:
    build: .
    command: python rpc_email/server.py
    ports:
      - "50053:50053"

  socket-service:
    build: .
    command: python socket_service/main.py
    ports:
      - "8001:8001"
    depends_on:
      - redis-socket-io
      - rpc-info-server

  api-gateway:
    build: .
    command: python api_gateway/main.py
    ports:
      - "8000:8000"
    depends_on:
      - rpc-report-server
      - rpc-email-server

volumes:
  redis-rpc-info-data:
  redis-socket-io-data:
```

**Ejecutar**:
```bash
docker-compose up -d
```

## Despliegue en la Nube

### AWS EC2

1. **Lanzar instancia EC2** (Ubuntu 22.04 LTS, t3.medium o superior)
2. **Configurar Security Groups** para permitir puertos 80, 443, 8000, 8001
3. **Conectar por SSH** y seguir pasos de [Despliegue en Producción](#despliegue-en-producción)
4. **Configurar Elastic IP** para IP estática

### Google Cloud Platform

1. **Crear instancia Compute Engine** (e2-medium o superior)
2. **Configurar Firewall Rules**
3. **Seguir pasos de despliegue en producción**

### Heroku

1. **Instalar Heroku CLI**
2. **Crear `Procfile`**:
```
web: python api_gateway/main.py
worker: python rpc_info/workers.py
rpc-info: python rpc_info/server.py
rpc-report: python rpc_report/server.py
rpc-email: python rpc_email/server.py
socket: python socket_service/main.py
```

3. **Desplegar**:
```bash
heroku create tu-app
git push heroku main
```

### DigitalOcean

1. **Crear Droplet** (Ubuntu, 4GB RAM mínimo)
2. **Seguir pasos de despliegue en producción**
3. **Configurar dominio** en el panel de control

## Configuración de Nginx

### Instalación

```bash
sudo apt install nginx
```

### Configuración

Edita `/etc/nginx/sites-available/cripto-rpc`:

```nginx
upstream api_gateway {
    server 127.0.0.1:8000;
}

upstream socket_server {
    server 127.0.0.1:8001;
}

server {
    listen 80;
    server_name tu-dominio.com;

    # Redirección a HTTPS (opcional)
    # return 301 https://$server_name$request_uri;

    location /api/ {
        proxy_pass http://api_gateway;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /socket.io/ {
        proxy_pass http://socket_server;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }

    location / {
        # Servir cliente web estático o proxy
        root /opt/cripto-rpc/client/dist;
        try_files $uri $uri/ /index.html;
    }
}
```

**Activar configuración**:
```bash
sudo ln -s /etc/nginx/sites-available/cripto-rpc /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL con Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d tu-dominio.com
```

## Monitoreo y Logs

### Logs

Los logs se guardan en `logs/`:
- `api_gateway.log`
- `rpc_info_server.log`
- `rpc_info_workers.log`
- `rpc_report_server.log`
- `rpc_email_server.log`
- `socket_service.log`

### Monitoreo con PM2 (Opcional)

```bash
npm install -g pm2

# Iniciar servicios con PM2
pm2 start rpc_info/server.py --name rpc-info --interpreter python3
pm2 start rpc_report/server.py --name rpc-report --interpreter python3
pm2 start rpc_email/server.py --name rpc-email --interpreter python3
pm2 start socket_service/main.py --name socket-service --interpreter python3
pm2 start api_gateway/main.py --name api-gateway --interpreter python3

# Guardar configuración
pm2 save
pm2 startup
```

### Health Checks

```bash
# API Gateway
curl http://localhost:8000/health

# Verificar servicios
systemctl status rpc-info
systemctl status api-gateway
```

## Backup y Recuperación

### Backup de Redis

```bash
# Backup manual
docker exec redis-rpc-info redis-cli SAVE
docker cp redis-rpc-info:/data/dump.rdb ./backup/
```

### Backup de Configuración

```bash
tar -czf backup-$(date +%Y%m%d).tar.gz .env logs/ nginx/
```

## Actualización

```bash
# Detener servicios
sudo systemctl stop rpc-info rpc-report rpc-email socket-service api-gateway

# Actualizar código
git pull origin main

# Recompilar protos
compile_proto.bat  # Windows
# o comandos manuales en Linux/Mac

# Reiniciar servicios
sudo systemctl start rpc-info rpc-report rpc-email socket-service api-gateway
```

## Troubleshooting

### Servicios no inician

```bash
# Ver logs
journalctl -u rpc-info -n 50
tail -f logs/rpc_info_server.log
```

### Redis no conecta

```bash
# Verificar contenedores
docker ps
docker logs redis-rpc-info
```

### Puerto ocupado

```bash
# Encontrar proceso
sudo lsof -i :8000
# Matar proceso
sudo kill -9 <PID>
```

## Seguridad

- ✅ Usar HTTPS en producción
- ✅ Configurar firewall
- ✅ No exponer puertos RPC públicamente
- ✅ Usar variables de entorno para credenciales
- ✅ Implementar rate limiting
- ✅ Validar todas las entradas
- ✅ Mantener dependencias actualizadas

## Soporte

Para problemas o preguntas:
- Abre un issue en GitHub
- Revisa la documentación en `docs/`
- Consulta los logs en `logs/`

