from fastapi import Request
from logger import logger
import time

async def log_middleware(request: Request, call_next):
    #Se crea un timer para poder logear cuánto tarda cada request que se le hace a la API en ser completado
    start = time.time()
    #Esperamos que la API reciba el response de el request que se haga
    response = await call_next(request)

    #Restamos el tiempo que ha transcurrido para obtener cuánto ha pa pasado desde que se inició el request
    process_time = time.time() - start
    
    #Formulamos un diccionario de datos para logs. Incluimos los parámetros que queremos que se vean en el log
    log_dict = {
        'url': request.url.path,
        'method': request.method,
        'process_time': process_time
    }
    #Logueamos en base al diccionario. Añadimos el parametro "extra" = log_dict para que cada parámetro del diccionario también se trate como una variable individual
    logger.info(log_dict, extra=log_dict)
    return response