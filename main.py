from fastapi import FastAPI
# Ajuste para una estructura de paquetes; reemplace 'my_fastapi_app' por el nombre de tu paquete
from routes import router as api_router
from dotenv import load_dotenv
import os
import logging

# Configura el logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Carga las variables de entorno desde .env
load_dotenv()

app = FastAPI()

app.include_router(api_router)