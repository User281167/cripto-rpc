@echo off
REM Script para compilar archivos .proto en Windows
REM Uso: compile_proto.bat

echo ==========================================
echo Compilando archivos Protocol Buffers
echo ==========================================
echo.

REM Verificar que grpcio-tools está instalado
python -c "import grpc_tools.protoc" 2>nul
if errorlevel 1 (
    echo grpcio-tools no esta instalado. Instalando...
    pip install grpcio-tools==1.76.0
    if errorlevel 1 (
        echo Error al instalar grpcio-tools
        pause
        exit /b 1
    )
)

REM Limpiar y crear directorio generated
if exist generated rmdir /s /q generated
mkdir generated
echo. > generated\__init__.py

echo Compilando crypto.proto...
python -m grpc_tools.protoc -I./proto --python_out=./generated --grpc_python_out=./generated ./proto/crypto.proto
if errorlevel 1 (
    echo Error compilando crypto.proto
    pause
    exit /b 1
)

echo Compilando report.proto...
python -m grpc_tools.protoc -I./proto --python_out=./generated --grpc_python_out=./generated ./proto/report.proto
if errorlevel 1 (
    echo Error compilando report.proto
    pause
    exit /b 1
)

echo Compilando email.proto...
python -m grpc_tools.protoc -I./proto --python_out=./generated --grpc_python_out=./generated ./proto/email.proto
if errorlevel 1 (
    echo Error compilando email.proto
    pause
    exit /b 1
)

echo.
echo Corrigiendo importaciones...

REM Corregir importaciones en crypto_pb2_grpc.py
powershell -Command "(Get-Content generated\crypto_pb2_grpc.py) -replace 'import crypto_pb2 as crypto__pb2', 'from . import crypto_pb2 as crypto__pb2' | Set-Content generated\crypto_pb2_grpc.py"

REM Corregir importaciones en report_pb2_grpc.py
powershell -Command "(Get-Content generated\report_pb2_grpc.py) -replace 'import report_pb2 as report__pb2', 'from . import report_pb2 as report__pb2' | Set-Content generated\report_pb2_grpc.py"

REM Corregir importaciones en email_pb2_grpc.py
powershell -Command "(Get-Content generated\email_pb2_grpc.py) -replace 'import email_pb2 as email__pb2', 'from . import email_pb2 as email__pb2' | Set-Content generated\email_pb2_grpc.py"

echo.
echo ==========================================
echo Compilacion completada exitosamente
echo ==========================================
echo.
pause
