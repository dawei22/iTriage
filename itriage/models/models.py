import infermedica_api
from infermedica_api.exceptions import MissingConfiguration
from itriage.utils import logger


# TODO: Cada vez que haya un cambio en el modelo, deberia guardarse en una BD para respaldo
class BasicUserModel:
    def __init__(self, api_model, api_version, app_id, app_key, disable_groups=False):

        # Represent user data
        self.user_profile = self.UserProfile()
        self.actual_diagnosis = infermedica_api.Diagnosis(sex="", age=0)
        self.actual_diagnosis.set_extras(attribute="disable_groups", value=disable_groups)
        self.triage = None

        # Infermedica API configuration
        infermedica_api.configure(app_id=app_id, app_key=app_key,
                                  model=api_model,
                                  api_version=api_version)

        try:
            self.infermedica_api = infermedica_api.get_api()
        except MissingConfiguration as e:
            # TODO: esta excepcion no esta funcionando
            logger.critical(str(e))
            raise Exception

    def set_sex_and_age(self):
        self.actual_diagnosis.patient_sex = self.user_profile.data["sex"]
        self.actual_diagnosis.patient_age = int(self.user_profile.data["age"])

    def call_risk_factor(self):
        """
        Get risk factor list
        :return:
        """
        try:
            return self.infermedica_api.risk_factors_list()
        except Exception as e:
            logger.critical(str(e))

    def call_diagnosis(self):
        """
        Send a diagnosis request with actual evidence. Get new questions to user
        :return:
        """
        try:
            self.actual_diagnosis = self.infermedica_api.diagnosis(self.actual_diagnosis)
        except Exception as e:
            logger.critical(str(e))

    def call_triage(self):
        """
        Get Triage with actual evidence
        :return:
        """
        try:
            self.triage = self.infermedica_api.triage(self.actual_diagnosis)
        except Exception as e:
            logger.critical(str(e))

    def get_new_diagnosis_questions(self):
        return self.actual_diagnosis.question

    def get_new_profile_questions(self):
        try:
            return next(self.user_profile.iter_dict_question)
        except StopIteration as e:
            logger.critical(str(e))

    def get_triage(self):
        return self.triage

    def add_evidence(self, id, choice_id):
        self.actual_diagnosis.add_evidence(_id=id, state=choice_id)

    def add_user_info(self, id, choice_id):
        try:
            self.user_profile.data[id] = choice_id
        except KeyError as e:
            logger.critical(str(e))

    def should_stop_diagnosis(self):
        return self.actual_diagnosis.should_stop

    def should_stop_sign_up(self):
        return self.user_profile.should_stop()

    def reset_model(self):
        self.actual_diagnosis = infermedica_api.Diagnosis(sex="", age=0)
        self.user_profile = self.UserProfile()

    class UserProfile:
        """
        To store all kind of non-medical data related to user eg. city,
        Any new attribute must have a ask_"name" method that returns a dict like this

        question =  {
            "type": None,
            "text": None,
            "items": [
                {
                    "id": None,
                    "name": None,
                    "choices": [
                        {
                            "id": None,
                            "label": None
                        },
                        {
                            "id": None,
                            "label": None
                        }

                    ]
                }
            ]
        }
        """

        def __init__(self):
            self.data = {
                "age": None,
                "sex": None
            }
            self.dict_question = [self.ask_age(), self.ask_sex(), ]
            self.iter_dict_question = iter(self.dict_question)

        def should_stop(self):
            return False if None in self.data.values() else True

        def ask_age(self):
            question = {
                "type": "single",
                "text": "Cuál es tu edad? ",
                "items": [
                    {
                        "id": "age",
                        "name": "",
                        "choices": []
                    }
                ]
            }
            return question

        def ask_sex(self):
            question = {
                "type": "single",
                "text": "Cuál es tu sexo biológico? ",
                "items": [
                    {
                        "id": "sex",
                        "name": "",
                        "choices": [
                            {
                                "id": "male",
                                "label": "Masculino"
                            },
                            {
                                "id": "female",
                                "label": "Femenino"
                            }
                        ]
                    }

                ]
            }
            return question
