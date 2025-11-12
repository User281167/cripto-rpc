import os
import sys
import io
import logging
from typing import Optional

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

from utils import RpcReportClient, RpcEmailClient, ProjectEnv

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

log = logging.getLogger(__name__)

app = FastAPI(
    title="Crypto RPC API Gateway",
    description="API Gateway para el sistema distribuido de reportes financieros",
    version="1.0.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar clientes RPC
rpc_report = RpcReportClient()
rpc_email = RpcEmailClient()


# Modelos de datos
class SubscriptionRequest(BaseModel):
    email: EmailStr
    hour: int
    minute: int


class UnsubscriptionRequest(BaseModel):
    email: EmailStr


# Endpoints de reportes
@app.get("/api/reports/crypto")
async def get_crypto_report(currency: str = Query(default="usd", description="Divisa (usd, eur, etc.)")):
    """
    Genera y descarga un reporte de criptomonedas en formato Excel (.xlsx)
    """
    try:
        log.info(f"Solicitando reporte crypto en {currency}")
        report = rpc_report.generate_crypto_report(currency)
        
        return StreamingResponse(
            io.BytesIO(report.content),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={report.filename}"}
        )
    except Exception as e:
        log.error(f"Error generando reporte crypto: {e}")
        raise HTTPException(status_code=500, detail=f"Error al generar el reporte: {str(e)}")


@app.get("/api/reports/trend")
async def get_trend_report(currency: str = Query(default="usd", description="Divisa (usd, eur, etc.)")):
    """
    Genera y descarga un reporte de tendencias en formato Word (.docx)
    """
    try:
        log.info(f"Solicitando reporte de tendencias en {currency}")
        report = rpc_report.generate_trend_report(currency)
        
        return StreamingResponse(
            io.BytesIO(report.content),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={report.filename}"}
        )
    except Exception as e:
        log.error(f"Error generando reporte de tendencias: {e}")
        raise HTTPException(status_code=500, detail=f"Error al generar el reporte: {str(e)}")


@app.get("/api/reports/executive")
async def get_executive_report(currency: str = Query(default="usd", description="Divisa (usd, eur, etc.)")):
    """
    Genera y descarga un reporte ejecutivo en formato PDF (.pdf)
    """
    try:
        log.info(f"Solicitando reporte ejecutivo en {currency}")
        report = rpc_report.generate_executive_report(currency)
        
        return StreamingResponse(
            io.BytesIO(report.content),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={report.filename}"}
        )
    except Exception as e:
        log.error(f"Error generando reporte ejecutivo: {e}")
        raise HTTPException(status_code=500, detail=f"Error al generar el reporte: {str(e)}")


@app.get("/api/reports/graph")
async def get_bar_graph(currency: str = Query(default="usd", description="Divisa (usd, eur, etc.)")):
    """
    Genera y descarga un gráfico de barras en formato PNG (.png)
    """
    try:
        log.info(f"Solicitando gráfico de barras en {currency}")
        report = rpc_report.generate_bar_graph(currency)
        
        return StreamingResponse(
            io.BytesIO(report.content),
            media_type="image/png",
            headers={"Content-Disposition": f"attachment; filename={report.filename}"}
        )
    except Exception as e:
        log.error(f"Error generando gráfico: {e}")
        raise HTTPException(status_code=500, detail=f"Error al generar el gráfico: {str(e)}")


# Endpoints de suscripción
@app.post("/api/subscriptions")
async def subscribe(subscription: SubscriptionRequest):
    """
    Suscribe un correo electrónico para recibir reportes diarios
    """
    try:
        log.info(f"Suscribiendo correo: {subscription.email}")
        response = rpc_email.subscribe_email(
            subscription.email,
            subscription.hour,
            subscription.minute
        )
        
        if not response.success:
            raise HTTPException(status_code=400, detail=response.message)
        
        return {"success": True, "message": response.message}
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error en suscripción: {e}")
        raise HTTPException(status_code=500, detail=f"Error al procesar la suscripción: {str(e)}")


@app.delete("/api/subscriptions")
async def unsubscribe(unsubscription: UnsubscriptionRequest):
    """
    Cancela la suscripción de un correo electrónico
    """
    try:
        log.info(f"Cancelando suscripción: {unsubscription.email}")
        response = rpc_email.unsubscribe_email(unsubscription.email)
        
        return {"success": True, "message": response.message}
    except Exception as e:
        log.error(f"Error cancelando suscripción: {e}")
        raise HTTPException(status_code=500, detail=f"Error al cancelar la suscripción: {str(e)}")


# Endpoint de health check
@app.get("/health")
async def health_check():
    """
    Verifica el estado del API Gateway
    """
    return {"status": "healthy", "service": "api-gateway"}


if __name__ == "__main__":
    import uvicorn
    
    port = int(ProjectEnv.BACKEND_PORT)
    log.info(f"Iniciando API Gateway en {ProjectEnv.BACKEND_HOST}:{port}")
    
    uvicorn.run(
        "main:app",
        host=ProjectEnv.BACKEND_HOST,
        port=port,
        reload=True
    )
