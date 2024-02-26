# FastAPI WhatsApp Integration

## Introduction
This project integrates WhatsApp messaging with a FastAPI application, enabling the sending and receiving of messages, images, audio, and videos through WhatsApp. It leverages the WhatsApp Business API to process incoming webhook events and allows media handling and response strategies.

## Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourgithubusername/yourrepositoryname.git](https://github.com/SergioROJ/SanosAPI)

2. **Instalar dependencias**
   ```bash
  pip install -r requirements.txt

3. **Variables de entorno**
  Es necesario que las siguientes variables de entorno hayan sido correctamente manejadas dentro del proyecto:

   ```bash
  USER_ACCESS_TOKEN=YourUserAccessToken
  PHONE_NUMBER_ID=YourPhoneNumberID
  VERSION=YourAPIVersion

  Estas variables de entorno deben provenir desde la aplicación que se debe haber creado en WhatsApp Bussines for Developers.

5. **Instancia de Ngrok**
  La API utiliza webhooks para poder realizar algunas de sus funcionalidades, como el manejo de eventos. Para poder utilizar el manejo de eventos es necesario tener un servidor público que se comunique con WhatsApp. Para esto Ngrok es utilizado. Ngrok permite que un servidor que está siendo utilizado localmente salga a internet para comunicarse, en este caso, con el manejo de webhooks de WhatsApp. Es necesario la instalación y configuración de su propia instancia de Ngrok para que la API pueda funcionar.

  4. **Correr la aplicación**
   ```bash
  uvicorn main:app --reload --port ####

  Se corre la aplicación en el puerto deseado. El flag de --reload habilita la recarga automática del servidor al hacer cambios en el código.
  
