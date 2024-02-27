from fastapi import FastAPI
# Asegúrate de ajustar el importe de router según la estructura de tu proyecto
from routes import router as api_router  # Importa el router de la aplicación desde el módulo de rutas
from dotenv import load_dotenv  # Importa la función para cargar variables de entorno desde archivos .env
import os  # Importa el módulo os para trabajar con variables de entorno y otras funcionalidades del sistema operativo
import logging  # Importa el módulo logging para configurar el registro de logs

# Configura el sistema de logging para la aplicación
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Carga las variables de entorno desde el archivo .env
# Esto es útil para mantener configuraciones sensibles o específicas del entorno fuera del código fuente
load_dotenv()

# Crea una instancia de la aplicación FastAPI
app = FastAPI()

# Incluye el router de la API en la aplicación
# Esto registra todas las rutas y operaciones definidas en el router con la aplicación FastAPI
app.include_router(api_router)
