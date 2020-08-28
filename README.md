# iTriage
> Librería para implementar un chatbot usando 
> el motor de chequeo de síntomas [Infermedica](https://infermedica.com)


Etapas y mensajes necesarios para implementar una máquina de estados para una
entrevista vía chatbot, con el fin de realizar un pre-diagnóstico en base
a síntomas. Por ahora solo disponible para COVID19. 

Se utiliza la [API](https://developer.infermedica.com/docs/introduction) para inferencia de Infermedica. 

## Pre-Requisitos

Se require crear un usuario en el portal para desarrolladores de [Infermedica](https://developer.infermedica.com/). 
Con esto se obtendra una APP-KEY y APP-ID por usuario.

## Instalación

- Se requiere Python 3.6+. Se recomienda crear un ambiente virtual.
- Clonar repositorio e instalar librerias necesarias.

```sh
pip install -r requirements.txt
```
## Inicio rapido
```
from itriage import Covid
from itriage.messages import BasicMessage

# Instanciar motor de entrevista con credenciales otorgadas por Infermedica
interview_engine = Covid(infermedica_app_id="XXX",infermedica_app_key="XXX")

# Se requiere instanciar un mensaje el cual se le pasara al motor
request = BasicMessage(user_id="<USERNAME>", _type=Types.TEXT)

While 1:

    # El motor procesara el mensaje enviado y generara una pregunta al usuario
    response = interview_engine.handle_message(request=request)
    
    # Desplegar pregunta a usuario y obtener una respuesta
    ...

    # Generar nueva consulta al motor
    # Para generar, se debe indicar el tipo de pregunta realizada. Esto 
    # se obtiene al procesar la respuesta anteriormente obtenida
    # Adicionalmente, se debe indicar el id de la pregunta realizada (Tambien
    obtenido previamente) y la respuesta obtenida de acuerdo a las opciones
    # ofrecidas

    request = BasicMessage(user_id="<USERNAME>", _type=<TYPES>)
    request.add_answer(_id=<id>, choice_id=<choice>)
```

Dentro de la carpeta **examples** se pueden encontrar una demo que simula un chat
en una terminal.

#### Terminal

En la carpeta **examples** ejecutar
```sh
python main.py
```

Esto iniciará la conversación. Seguir las instrucciones que se desplieguen
en la terminal.

## Conexion con Apps
### Slack

![](slack_example.JPG)

Un ejemplo de integracion a modo de bot es con Slack. Se incluye una demo en la 
cual se utiliza un servidor local usando Flask como backend. La conexion es mediante
la API de slack. Esta habilitado para conversaciones via DM al bot.

### Pre-requisitos
#### Configurar slack bot
- [Crear]((https://github.com/slackapi/python-slackclient/blob/main/tutorial/01-creating-the-slack-app.md)) una app en Slack y agregarla al espacio de trabajo.
- Se requiere que el backend este disponible para acceder publicamente. Una opcion es usar [Ngrok](https://medium.com/better-programming/ngrok-make-your-localhost-accessible-to-anyone-333b99e44b07) para generar un tunel.
Otra alternativa es montar en un servidor. Para esta demo se utilizo la primera opcion, pero para uso en produccion se debe optar por la segunda.
- [Crear](https://api.slack.com/interactivity/slash-commands)  un comando Slash `/triage`. 
Entregar como Request URL la direccion generada por Ngrok.
- Revisar en el panel de control del bot (Features - OAuth & Permissions) si tiene los siguientes permisos. Si no estan, habilitarlos.

![](examples_slack/scope.JPG)

#### Configurar servidor local
- `pip install Flask==1.1.2`
- `pip install slackclient==2.6.0`
- Agregar en `examples_slack/utils/config.py` las variables de acceso a la app. Se puede obtener
tal cual se muestra [aca.](https://github.com/slackapi/python-slackclient/blob/main/tutorial/04-running-the-app.md) 
```
SLACK_BOT_TOKEN = "xoxb-xxxxxxxxxxxxxxxxxxxx"
SLACK_VERIFICATION_TOKEN = "xxxxxxxxxxxxxx"
SLACK_SIGNING_SECRET = "xxxxxxxxxxxxxxxx"
```

### Demo

Con el localhost visible publicamente, ir a `examples_slack` y ejecutar
```python server.py```. Luego, desde el DM con la app, ejecutar `/triage` y 
comenzara la conversacion.



## Extensiones

Para adecuar a uso personal, se debe 

- Implementar un instancia que guie la conversacion. Esta debe heredar de `BaseInterview`
- Implementar estados customizados heredando de `BaseState`


## Historial de versiones

* 1.0.0
    * Triage covid19

## Autor
* [David Gómez](https://github.com/dawei22/Carguio)

## Licencia
MIT License

