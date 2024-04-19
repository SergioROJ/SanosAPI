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
  Es necesario que las variables de entorno hayan sido correctamente creadas en su archivo .env. El contenido de estas variables de entorno deben provenir desde la aplicación que se debe haber creado en WhatsApp Bussines for Developers. Igualmente, es necesario tener la el proyecto de Mailjet y de Twitter creados para sus respectivas variables de entorno.

   ```bash
   BUSINESS_ID=YourBussinesID
   PHONE_NUMBER_ID=YourPhoneNumberID
   USER_ACCESS_TOKEN=YourUserAccessToken
   PHONE_NUMBER_ID=YourPhoneNumberID
   WABA_ID=YourWABAID
   VERSION=YourAPIVersion
   MAILJET_KEY=YourMailjetKey
   MAILJET_SECRET=YourMailjetSecret
   TWITTER_CONSUMER_KEY=YourTwitterConsumerKey
   TWITTER_CONSUMER_SECRET=YourTwitterConsumerSecret
   TWITTER_ACCESS_TOKEN=YourTwitterAccessToken
   TWITTER_TOKEN_SECRET=YourTwitterTokenSecret
   TWITTER_BEARER_TOKEN=YourTwitterBearerToken

4. **Instancia de Ngrok**
  La API utiliza webhooks para poder realizar algunas de sus funcionalidades, como el manejo de eventos. Para poder utilizar el manejo de eventos es necesario tener un servidor público que se comunique con WhatsApp. Para esto Ngrok es utilizado. Ngrok permite que un servidor que está siendo utilizado localmente salga a internet para comunicarse, en este caso, con el manejo de webhooks de WhatsApp. Es necesario la instalación y configuración de su propia instancia de Ngrok para que la API pueda funcionar. Una vez se haya configurado la instancia de ngrok, para ejecutarla se corre el siguiente comando:

   ```bash
   ngrok http #numero_de_puerto_donde_corre_la_API el-link-de.tu-instancia-de.ngork-free.app

   La otra alternativa es exponer el puerto del servidor a internet para poder tener contacto con WhatsApp.

5. **Prometheus y Grafana**
   La API está pensada para poder integrar Prometheus y Grafana para monitoreo, métricas y dashboards. Para esto, y por otras razones, la aplicación se sube en contenedores de docker. La configuración de estos servicios, y de la API en sí, se encuentran en el Dockerfile y en el docker_compose.yml. A la hora de subir la aplicación con docker, sencillamente se necesita correr el comando:

   ```bash
   docker compose up

6. **Configuraciones extras**
   Si se desea correr la aplicación en otros puertos, solo es necesario cambiar la línea donde se despliega el API mediante uvicorn en el Dockerfile:

   ```bash
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]

   Por otro lado, también será necesario cambiar el puerto expuesto para Docker:

   ```bash
   EXPOSE 5000
  
