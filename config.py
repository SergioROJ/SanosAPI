import os
from dotenv import load_dotenv

# Carga las variables de entorno desde .env en desarrollo
load_dotenv()

class Config:
    BUSINESS_ID = os.getenv('BUSINESS_ID', 'default_value')
    PHONE_NUMBER_ID = os.getenv('PHONE_NUMBER_ID', 'default_value')
    RECIPIENT_PHONE_NUMBER = os.getenv('RECIPIENT_PHONE_NUMBER', 'default_value')
    USER_ACCESS_TOKEN = os.getenv('USER_ACCESS_TOKEN', 'default_value')
    WABA_ID = os.getenv('WABA_ID', 'default_value')
    VERSION = os.getenv('VERSION', 'v18.0')