"""
Define every text message that we want to send to user. Message will be display when enter a new state o leave it
To guide conversation

Instructions:

1. Define which state are you going to use
2. Define if message need to be show when entering to state or exiting
3. Create a variable and assing it the message
        variable = "hello"

    if you need to add user name inside message, put {0} instead. Code will automatic fill it

4. Push variable to a list

    template_chat_dict[NAME OF STATE]["on_enter" or "on_exit].append(VARIABLE NAME)

See examples below

"""

from itriage.utils import INIT_STATE_NAME, CREATEUSER_STATE_NAME, RISKFACTOR_STATE_NAME, DIAGNOSIS_STATE_NAME, \
    TRIAGE_STATE_NAME

template_chat_dict = {}

### Init
template_chat_dict[INIT_STATE_NAME] = {
    "on_enter": [],
    "on_exit": []
}

## On enter

## On exit

# Don't change {0}. It will have user id
say_hi = "Hola {0}! \n" \
         "Te entregaré el riesgo de tener COVID19 \n" \
         "y los pasos a seguir \n" \
         "\n" \
         "Por favor ingrese los datos que se pediran \n" \
         "para crear su perfil \n" \
         "\n"

template_chat_dict[INIT_STATE_NAME]["on_exit"].append(say_hi)

### Create User
template_chat_dict[CREATEUSER_STATE_NAME] = {
    "on_enter": [],
    "on_exit": []
}

## On enter

## On exit

say_bye = "Gracias {0}!"
template_chat_dict[CREATEUSER_STATE_NAME]["on_exit"].append(say_bye)

### Risk Factor
template_chat_dict[RISKFACTOR_STATE_NAME] = {
    "on_enter": [],
    "on_exit": []
}

## On enter

## On exit


### Diagnosis
template_chat_dict[DIAGNOSIS_STATE_NAME] = {
    "on_enter": [],
    "on_exit": []
}

## On enter

start_interview = "Empieza la entrevista !"
template_chat_dict[DIAGNOSIS_STATE_NAME]["on_enter"].append(start_interview)

## On exit

no_more_interview = " Gracias por la información! " \
                    " Hemos recopilado la suficiente información. " \
                    "A continuación se mostrarán tus resultados :" \
                    "" \
                    ""
template_chat_dict[DIAGNOSIS_STATE_NAME]["on_exit"].append(no_more_interview)

### Triage
template_chat_dict[TRIAGE_STATE_NAME] = {
    "on_enter": [],
    "on_exit": []
}
## On enter

## On exit
