@echo off
REM Script Batch para iniciar todos los servicios en Windows
REM Uso: start_services.bat

echo ==========================================
echo Iniciando Sistema Distribuido Crypto RPC
echo ==========================================
echo.

REM Crear directorio para logs
if not exist logs mkdir logs

echo 1. Verificando contenedores Docker...
echo --------------------------------------

REM Iniciar Redis para rpc_info
docker ps | findstr redis-rpc-info >nul 2>&1
if errorlevel 1 (
    echo Iniciando Redis para rpc_info...
    docker run -d --name redis-rpc-info -p 6380:6379 redis:7 >nul 2>&1
    if errorlevel 1 (
        docker start redis-rpc-info >nul 2>&1
    )
) else (
    echo Redis rpc_info ya esta corriendo
)

REM Iniciar Redis para socket_service
docker ps | findstr redis-socket-io >nul 2>&1
if errorlevel 1 (
    echo Iniciando Redis para socket_service...
    docker run -d --name redis-socket-io -p 6381:6379 redis:7 >nul 2>&1
    if errorlevel 1 (
        docker start redis-socket-io >nul 2>&1
    )
) else (
    echo Redis socket_service ya esta corriendo
)

timeout /t 2 /nobreak >nul

echo.
echo 2. Iniciando servicios RPC...
echo ------------------------------

REM Iniciar workers de rpc_info
echo Iniciando rpc_info_workers...
start /B python rpc_info/workers.py > logs/rpc_info_workers.log 2>&1

REM Iniciar servidor rpc_info
echo Iniciando rpc_info_server...
start /B python rpc_info/server.py > logs/rpc_info_server.log 2>&1

REM Iniciar servidor rpc_report
echo Iniciando rpc_report_server...
start /B python rpc_report/server.py > logs/rpc_report_server.log 2>&1

REM Iniciar servidor rpc_email
echo Iniciando rpc_email_server...
start /B python rpc_email/server.py > logs/rpc_email_server.log 2>&1

timeout /t 2 /nobreak >nul

echo.
echo 3. Iniciando servicios web...
echo ------------------------------

REM Iniciar socket_service
echo Iniciando socket_service...
start /B python socket_service/main.py > logs/socket_service.log 2>&1

REM Iniciar API Gateway
echo Iniciando api_gateway...
start /B python api_gateway/main.py > logs/api_gateway.log 2>&1

timeout /t 2 /nobreak >nul

echo.
echo ==========================================
echo Todos los servicios iniciados
echo ==========================================
echo.
echo Servicios corriendo:
echo   - RPC Info (gRPC):    127.0.0.1:50051
echo   - RPC Report (gRPC):  127.0.0.1:50052
echo   - RPC Email (gRPC):   127.0.0.1:50053
echo   - Socket Service:     127.0.0.1:8001
echo   - API Gateway:        127.0.0.1:8000
echo.
echo Logs disponibles en el directorio: logs/
echo.
echo Para detener los servicios, cierra esta ventana o usa Ctrl+C
echo.
pause

@echo off
REM Script para iniciar Nginx en Windows
REM Uso: start_nginx.bat

echo ==========================================
echo Iniciando Nginx
echo ==========================================
echo.

REM Verificar si Nginx está instalado
where nginx >nul 2>&1
if errorlevel 1 (
    echo Error: Nginx no esta instalado
    echo.
    echo Descarga Nginx para Windows desde:
    echo https://nginx.org/en/download.html
    echo.
    echo Instrucciones:
    echo 1. Descarga la version estable de Nginx para Windows
    echo 2. Extrae el archivo ZIP en C:\nginx
    echo 3. Agrega C:\nginx a la variable PATH del sistema
    echo.
    pause
    exit /b 1
)

REM Detener Nginx si está corriendo
nginx -s quit >nul 2>&1

REM Copiar configuración al directorio de Nginx
echo Configurando Nginx...
REM Usar sintaxis segura y expansión retardada para evitar errores cuando la ruta contiene paréntesis
setlocal enabledelayedexpansion
set "NGINX_CONF=%~dp0nginx\nginx.conf"

if not exist "!NGINX_CONF!" (
    echo Error: No se encontro el archivo de configuracion
    echo Buscando en: !NGINX_CONF!
    pause
    exit /b 1
)

REM Iniciar Nginx con la configuración del proyecto
echo Iniciando Nginx con configuracion personalizada...
nginx -c "!NGINX_CONF!"

if errorlevel 1 (
    echo.
    echo Error al iniciar Nginx
    echo Verifica la configuracion con: nginx -t -c "!NGINX_CONF!"
    pause
    exit /b 1
)

echo.
echo ==========================================
echo Nginx iniciado correctamente
echo ==========================================
echo.
echo El sistema esta disponible en:
echo   - http://localhost/api/          (API REST)
echo   - http://localhost/socket.io/    (WebSocket)
echo   - http://localhost/health        (Health Check)
echo.
echo Para detener Nginx, ejecuta: nginx -s quit
echo.
pause