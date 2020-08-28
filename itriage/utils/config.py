##### Infermedica
## Keys
INFERMEDICA_APP_ID = "xxxxx"
INFERMEDICA_APP_KEY = "xxxxxxxxxxxx"

## For covid
API_VERSION_COVID = "covid19"
API_MODEL_SPANISH_LA = "infermedica-es-xl"

## States names
# Define states
INIT_STATE_NAME = "init"
CREATEUSER_STATE_NAME = "create"
RISKFACTOR_STATE_NAME = "risk factor"
DIAGNOSIS_STATE_NAME = "diagnosis"
TRIAGE_STATE_NAME = "itriage"

BOT_ID = "Doctor_us"

# Logger from transitions
import logging

logging.getLogger('transitions').setLevel(logging.DEBUG)

logger = logging.getLogger("myLogger")
logger.setLevel(logging.DEBUG)

c_handler = logging.StreamHandler()
c_handler.setLevel(logging.DEBUG)

c_format = logging.Formatter('%(threadName)s - %(levelname)s - %(funcName)s - %(message)s')
c_handler.setFormatter(c_format)

logger.addHandler(c_handler)
