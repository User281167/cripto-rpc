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
  - Librerías recomendadas: `RPyC`, `gRPC`, o `msgpack-rpc`.
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

## Instalación y Ejecución

1. Clonar el repositorio:
   git clone https://github.com/tuusuario/tu-repo.git
   cd tu-repo
   ```

2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Ejecutar el servidor FastAPI:
   ```bash
   uvicorn main:app --reload
   ```

4. Configurar el bot de Telegram y el servicio de correo.

---

## Contribuciones

Este proyecto está abierto a mejoras. Puedes contribuir con:

- Nuevos indicadores financieros.
- Mejoras en el diseño de reportes.
- Funcionalidades avanzadas del bot.
- Optimización de la arquitectura distribuida.

---

¿Quieres que te ayude a generar el `requirements.txt` o el `main.py` base para FastAPI y RPC? También puedo ayudarte a escribir el endpoint `/suscribirse` o el worker que consuma la cola.