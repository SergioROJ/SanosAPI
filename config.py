import os
from dotenv import load_dotenv

# Carga las variables de entorno desde un archivo .env en el entorno de desarrollo.
# Esto permite mantener las credenciales y otros datos sensibles fuera del código fuente.
load_dotenv()

class Config:
    """
    Clase de configuración para centralizar el acceso a las variables de entorno y otros valores de configuración.
    
    Atributos:
        BUSINESS_ID (str): ID del negocio utilizado en la integración con la API, con un valor predeterminado si no se encuentra.
        PHONE_NUMBER_ID (str): ID del número de teléfono asociado con la cuenta de WhatsApp Business API.
        RECIPIENT_PHONE_NUMBER (str): Número de teléfono del destinatario para el envío de mensajes, utilizado para pruebas o como valor predeterminado.
        USER_ACCESS_TOKEN (str): Token de acceso del usuario para autenticación con la API de WhatsApp.
        WABA_ID (str): WhatsApp Business Account ID necesario para algunas operaciones con la API.
        VERSION (str): Versión de la API de WhatsApp a utilizar, con un valor predeterminado de 'v18.0'.
        MAILJET_KEY (str): Token de acceso del usuario para la autenticación con la API de Mailjet
        MAILJET_SECRET (str): Cadena string secreta generada en el dashboard de Mailjet con el fin de poderse autenticar
    """
    
    BUSINESS_ID = os.getenv('BUSINESS_ID', 'default_value')
    PHONE_NUMBER_ID = os.getenv('PHONE_NUMBER_ID', 'default_value')
    RECIPIENT_PHONE_NUMBER = os.getenv('RECIPIENT_PHONE_NUMBER', 'default_value')
    USER_ACCESS_TOKEN = os.getenv('USER_ACCESS_TOKEN', 'default_value')
    WABA_ID = os.getenv('WABA_ID', 'default_value')
    VERSION = os.getenv('VERSION', 'v18.0')
    MAILJET_KEY = os.getenv('MAILJET_KEY', 'default_value')
    MAILJET_SECRET = os.getenv('MAILJET_SECRET', 'default_value')
