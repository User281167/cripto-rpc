# Ejecutar el proyecto localmente con todos los microservicios
# Ejecutar en segundo plano o mostrarlos en consola
# Permitir elegir los microservicios a mostrar o a ejecutar

# Ejemplo de uso:
# .\run.ps1 -d auth -r auth, user -> mostrar auth en consola externa y ejecutar auth y user

param (
    [string[]]$d = @(),  # Lista de servicios a mostrar en consola, null o vacío todos en segundo plano
    [string[]]$r = @(),  # Lista de servicios a ejecutar, null o vacío para todos
    [switch]$nginx       # Ejecutar y configurar nginx
)

Write-Host "Iniciando entorno local..."

if (-not (Test-Path ".venv")) {
    # crear entorno virtual
    Write-Host "Creando entorno virtual..."
    python -m venv .venv
}

$venvPath = "$PWD\.venv\Scripts\activate.ps1"
# Activar entorno virtual
& $venvPath

# Instalar dependencias
Write-Host "Instalando dependencias..."
python -m pip install -r requirements.txt

if (-not (Test-Path "logs")) {
    Write-Host "Creando directorio para logs..."
    New-Item -ItemType Directory -Path "logs"
}

# Cliente web
if (-not (Test-Path "./client/node_modules")) {
    Write-Host "Instalando cliente web..."
    npm install
}

# Si ejecuta nginx cambiar las .env del cliente
if ($nginx) {
    # archivo .env borrar contenido y agregar nuevas
    $envFile = "./client/.env"

    if (Test-Path $envFile) {
        Remove-Item $envFile
    }

    Add-Content $envFile "VITE_API_URL=http://localhost/api"
    Add-Content $envFile "VITE_SOCKET_URL=ws://localhost"
}

# Definir servicios
$services_list = @(
    @{ Name = "worker"; Path = "./rpc_info"; Script = "python -u workers.py" },
    @{ Name = "info"; Path = "./rpc_info"; Script = "python -u server.py" },
    @{ Name = "report"; Path = "./rpc_report"; Script = "python -u server.py" },
    @{ Name = "email"; Path = "./rpc_email"; Script = "python -u server.py" },
    @{ Name = "socket"; Path = "./socket_service"; Script = "python -u main.py" },
    @{ Name = "socket2"; Path = "./socket_service"; Script = "python -u main.py --port 8002" },
    @{ Name = "gateway"; Path = "./api_gateway"; Script = "python -u main.py" }
    @{ Name = "client"; Path = "./client"; Script = "npm run dev" }
)

$services = $services_list | Where-Object { $r -contains $_.Name -or $r.Count -eq 0 }
$pid = @()

# Ejecutar servicios según visibilidad
foreach ($svc in $services) {
    $fullCommand = "cd $($svc.Path); $($svc.Script)"
    $logFile = "$PWD\logs\$($svc.Name).log"

    # cliente abrir en consola
    if ($d -contains $svc.Name -or $svc.Name -eq "client") {
        Write-Host "Mostrando servicio: $($svc.Name)"
        $fullCommand = "cd $($svc.Path); $($svc.Script) | Tee-Object -FilePath '$($logFile)' -Append"
        Start-Process powershell -ArgumentList "-NoExit", "-Command", $fullCommand
    }
    else {
        Write-Host "Ejecutando en segundo plano: $($svc.Name)"
        $fullCommand = "cd $($svc.Path); &$($svc.Script) *> '$($logFile)'"
        Start-Process powershell -WindowStyle Hidden -ArgumentList "-Command", $fullCommand
    }
}

if ($nginx) {
    Write-Host "`nIniciando Nginx..."
    try {
        # Encontrar la ruta de instalación de Nginx
        $nginxPath = (Get-Command nginx).Source

        # La "raíz" o "prefix" de Nginx es el directorio donde está el .exe
        $nginxPrefix = Split-Path $nginxPath -Parent

        # Construir la ruta completa al archivo de configuración del proyecto
        $nginxConf = "$PWD\nginx\nginx.conf"

        if (-not (Test-Path $nginxConf)) {
            throw "El archivo de configuración de Nginx no se encontró en: $nginxConf"
        }

        # Detener cualquier instancia previa de Nginx para empezar de cero
        Start-Process -FilePath $nginxPath -ArgumentList "-p `"$nginxPrefix`" -s quit" -WindowStyle Hidden -Wait

        # Iniciar Nginx en segundo plano con la configuración del proyecto
        # -p le dice a Nginx cuál es su directorio base (para logs, etc.)
        # -c le dice qué archivo de configuración usar
        $arguments = "-p `"$nginxPrefix`" -c `"$nginxConf`""
        Start-Process -FilePath $nginxPath -ArgumentList $arguments -WindowStyle Hidden

        Write-Host "Nginx iniciado correctamente."
    } catch {
        Write-Host -ForegroundColor Red "Error al iniciar Nginx: $($_.Exception.Message)"
        Write-Host -ForegroundColor Yellow "Asegúrate de que Nginx esté instalado y en el PATH del sistema."
        Write-Host -ForegroundColor Yellow "Puede que necesites ejecutar este script como Administrador."
    }
}


Write-Host "`nTodos los servicios han sido lanzados."
Write-Host "Presiona ENTER para detenerlos..."
Read-Host

# Detener nginx
if ($nginx) {
    Write-Host "Deteniendo Nginx..."
    Start-Process -FilePath $nginxPath -ArgumentList "-p `"$nginxPrefix`" -s stop" -WindowStyle Hidden -Wait
    Write-Host "Nginx detenido."
}

# Detener servicios
Get-Job | Stop-Job
Get-Job | Remove-Job
Get-Process python | ForEach-Object {
    try {
        $_.CloseMainWindow() | Out-Null
        $_.Kill()
    } catch {
        Write-Host "No se pudo cerrar el proceso $($_.Id): $($_.Exception.Message)"
    }
}

Write-Host "Servicios detenidos."
