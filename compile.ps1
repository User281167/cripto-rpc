# .ps1 -ArgumentList "-info"

param (
    [switch]$info
)

if ($info.IsPresent) {
    # Compilar el archivo .proto
    python -m grpc_tools.protoc `
      -I ./rpc_info `
      --python_out=./rpc_info `
      --grpc_python_out=./rpc_info `
      ./rpc_info/crypto.proto

    # Verifica que la compilación fue exitosa
    if ((Test-Path "./rpc_info/crypto_pb2.py") -and (Test-Path "./rpc_info/crypto_pb2_grpc.py")) {
        Write-Host "Archivos generados correctamente."

        # Crear carpeta backend si no existe
        if (-not (Test-Path "./backend")) {
            New-Item -ItemType Directory -Path "./backend" | Out-Null
        }

        # Copiar los archivos al backend
        Copy-Item "./rpc_info/crypto_pb2.py" -Destination "./backend/" -Force
        Copy-Item "./rpc_info/crypto_pb2_grpc.py" -Destination "./backend/" -Force

        Write-Host "Archivos copiados a /backend/"
    } else {
        Write-Host "Error: No se generaron los archivos esperados."
    }
}

Write-Host "Compilacion exitosa."