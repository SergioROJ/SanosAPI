# FastAPI WhatsApp Integration

## Introducción
Este proyecto integra el envío y recepción de mensajes, imágenes, audio y videos a través de WhatsApp con una aplicación FastAPI. Utiliza la API de WhatsApp Business para procesar eventos entrantes de webhook y permite el manejo de medios y estrategias de respuesta.

## Setup
1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/SergioROJ/SanosAPI

2. **Instalar dependencias**
   Se recomienda instalarlos. Después de instalarlos, tenemos que dar upgrade a la última versión

   ```bash
   pip install -r requirements.txt

3. **Variables de entorno**
  Es necesario que las variables de entorno hayan sido correctamente creadas en su archivo .env. El contenido de estas variables de entorno deben provenir desde la aplicación que se debe haber creado en WhatsApp Bussines for Developers.

   ```bash
   USER_ACCESS_TOKEN=YourUserAccessToken
   PHONE_NUMBER_ID=YourPhoneNumberID
   VERSION=YourAPIVersion

4. **Instancia de Ngrok**
  La API utiliza webhooks para poder realizar algunas de sus funcionalidades, como el manejo de eventos. Para poder utilizar el manejo de eventos es necesario tener un servidor público que se comunique con WhatsApp. Para esto Ngrok es utilizado. Ngrok permite que un servidor que está siendo utilizado localmente salga a internet para comunicarse, en este caso, con el manejo de webhooks de WhatsApp. Es necesario la instalación y configuración de su propia instancia de Ngrok para que la API pueda funcionar. Una vez se haya configurado la instancia de ngrok, para ejecutarla se corre el siguiente comando:

   ```bash
   ngrok http #numero_de_puerto_donde_corre_la_API el-link-de.tu-instancia-de.ngork-free.app

5. **Correr la aplicación**
   Se corre la aplicación en el puerto deseado. El flag de --reload habilita la recarga automática del servidor al hacer cambios en el código.

   ```bash
   uvicorn main:app --reload --port ####

  
