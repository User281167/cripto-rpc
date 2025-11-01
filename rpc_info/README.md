# RPC Info

## Servicio gRPC
- Lista de criptomonedas
- Información de una cripto concreta

## Convertir .proto a .py
``` bash
cd crypto-rpc
python -m grpc_tools.protoc -I./rpc_info --python_out=./rpc_info --grpc_python_out=./rpc_info ./rpc_info/crypto.proto
```