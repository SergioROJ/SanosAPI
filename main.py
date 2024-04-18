from fastapi import FastAPI, Request
# Asegúrate de ajustar el importe de router según la estructura de tu proyecto
from routes import router as api_router  # Importa el router de la aplicación desde el módulo de rutas
from dotenv import load_dotenv  # Importa la función para cargar variables de entorno desde archivos .env
from prometheus_fastapi_instrumentator import Instrumentator
import os  # Importa el módulo os para trabajar con variables de entorno y otras funcionalidades del sistema operativo
from logger import logger
from middleware import log_middleware
from starlette.middleware.base import BaseHTTPMiddleware

# Carga las variables de entorno desde el archivo .env
# Esto es útil para mantener configuraciones sensibles o específicas del entorno fuera del código fuente
load_dotenv()
print("tes2t")
print("tes3t")
# Crea una instancia de la aplicación FastAPI
app = FastAPI()

app.add_middleware(BaseHTTPMiddleware, dispatch = log_middleware)
logger.info(f"#################################Inicializando API...#################################")
logger.info(f"#################################Inicializando API...#################################")
logger.info(f"#################################Inicializando API...#################################")
logger.info(f"#################################Inicializando API...#################################")


# Incluye el router de la API en la aplicación
# Esto registra todas las rutas y operaciones definidas en el router con la aplicación FastAPI
app.include_router(api_router)

Instrumentator().instrument(app).expose(app)