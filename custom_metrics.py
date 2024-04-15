import prometheus_client

class CustomMetricsPrometheus:

    Cantidad_mensajes_whatsapp_enviados = prometheus_client.Counter(
        "Cantidad_mensajes_whatsapp_enviados",
        "Cantidad de mensajes que han sido ENVIADOS por Whatsapp"
)

    Cantidad_mensajes_whatsapp_recibidos = prometheus_client.Counter(
        "Cantidad_mensajes_whatsapp_recibidos",
        "Cantidad de mensajes que han sido RECIBIDOS por Whatsapp"
)
    
    Mensajes_whatsapp_error = prometheus_client.Counter(
        "Mensajes_whatsapp_error",
        "Cantidad de mensajes que han retornado o dado origen a algún tipo de ERROR"
)
    
    Imagenes_recibidas_whatsapp = prometheus_client.Counter(
        "Imagenes_recibidas_whatsapp",
        "Cantidad de mensajes que han retornado o dado origen a algún tipo de ERROR"
)
    
    Videos_recibidas_whatsapp = prometheus_client.Counter(
        "Videos_recibidas_whatsapp",
        "Cantidad de mensajes que han retornado o dado origen a algún tipo de ERROR"
)
    
    Audios_recibidas_whatsapp = prometheus_client.Counter(
        "Audios_recibidas_whatsapp",
        "Cantidad de mensajes que han retornado o dado origen a algún tipo de ERROR"
)
    
    Documentos_recibidas_whatsapp = prometheus_client.Counter(
        "Documentos_recibidas_whatsapp",
        "Cantidad de mensajes que han retornado o dado origen a algún tipo de ERROR"
)
    
    Tweets_recibidos_whatsapp = prometheus_client.Counter(
        "Tweets_recibidos_whatsapp",
        "Cantidad de mensajes que han retornado o dado origen a algún tipo de ERROR"
    )