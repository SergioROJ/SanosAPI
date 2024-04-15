import logging  # Impopip instarta el módulo logging para configurar el registro de logs
import sys

# Configura el sistema de logging para la aplicación
logger = logging.getLogger()
formatter = logging.Formatter(
    fmt="%(asctime)s - %(levelname)s - %(message)s"
    )

stream_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler("app.log")

#Manejadores para los logs
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.handlers = [stream_handler, file_handler]
logger.setLevel(logging.INFO)