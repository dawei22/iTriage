import abc
from infermedica_api.models.diagnosis import DiagnosisQuestion
from transitions import State
from transitions.core import EventData
from itriage.messages import BasicMessage, Types, TypesQuestion
from itriage.models import BasicUserModel
from itriage.utils import BOT_ID, INIT_STATE_NAME, CREATEUSER_STATE_NAME, RISKFACTOR_STATE_NAME, DIAGNOSIS_STATE_NAME, \
    TRIAGE_STATE_NAME


class BaseState(State):
    """
    Base state with common functionalitys. Inherit it to create new states
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, name, on_enter=None, on_exit=None):
        super().__init__(name=name, on_exit=on_exit, on_enter=on_enter)
        self._change_state = False
        self._text_on_enter = []
        self._text_on_exit = []

    @abc.abstractmethod
    def handle(self, event):
        pass

    @property
    def change_state(self):
        return self._change_state

    @change_state.setter
    def change_state(self, b):
        self._change_state = b

    def _exit_state(self, event):
        """
        Execute when exit state. Generally, i'll be printing some text. In case that you need to do something else,
        override this method
        :param event:
        :type event: EventData
        :return:
        """

        request: BasicMessage = event.kwargs["request"]
        response: list = event.kwargs["response"]

        for text in self._text_on_exit:  # type:str
            response.append(self.create_text_msg(text=text.format(request.user_id)))

    def create_text_msg(self, text):
        """
        Create a text message to user
        :param text:
        :return:
        """
        return BasicMessage(user_id=BOT_ID, _type=Types.TEXT, text=text)

    def create_block_msg(self, payload):
        """
        Create a block msg to user with a pre-defined payload.
        Payload can be set as a dict or a DiagnosisQuestion
        :param payload:
        :return:
        """
        message = BasicMessage(user_id=BOT_ID, _type=Types.BLOCK)

        if isinstance(payload, dict):
            message.add_question(_type=self.map_type(payload["type"]), _text=payload["text"], _items=payload["items"])
            return message

        elif isinstance(payload, DiagnosisQuestion):
            message.add_question(_type=self.map_type(payload.type), _text=payload.text, _items=payload.items)
            return message

    def create_risf_factor_msg(self, payload):
        """
        Add every risk factor to message payload as a RiskFactor object

        :param payload: A list of risk factor
        :type payload: list
        :return: a msg encapsulated
        """
        message = BasicMessage(user_id=BOT_ID, _type=Types.BLOCK)
        for risk in payload:
            message.add_risk_factor(_id=risk["id"], _name=risk["name"], _question=risk["question"])
        return message

    def create_triage_msg(self, payload):
        """
        Create a block message to send itriage results
        :param payload:
        :type payload: dict
        :return:
        """
        message = BasicMessage(user_id=BOT_ID, _type=Types.BLOCK)
        if isinstance(payload, dict):
            message.add_triage(description=payload["description"], label=payload["label"], serious=payload["serious"],
                               triage_level=payload["triage_level"])
            return message

    @staticmethod
    def map_type(question_type):
        if question_type == TypesQuestion.GROUP_SINGLE.value:
            return TypesQuestion.GROUP_SINGLE
        elif question_type == TypesQuestion.GROUP_MULTIPLE.value:
            return TypesQuestion.GROUP_MULTIPLE
        elif question_type == TypesQuestion.SINGLE.value:
            return TypesQuestion.SINGLE

    def reset_data(self):
        """
        reset data for new interview

        :return:
        """
        self.change_state = False


class InitState(BaseState):

    def __init__(self, on_enter_msg, on_exit_msg):
        super().__init__(name=INIT_STATE_NAME, on_enter=[self._new_interview], on_exit=[self._exit_state])
        self._text_on_enter = on_enter_msg
        self._text_on_exit = on_exit_msg

    def handle(self, event):
        """
        Go to next state when reciving a empty message. Dump state
        :param event:
        :type event: EventData
        :return:
        """
        request: BasicMessage = event.kwargs["request"]
        if request:
            self.change_state = True

    def _new_interview(self, event):
        """
        If a new instance on interview is create, this method doesnt have any sense.
        When a old instance is reuse for a new interview, reset data

        :param event:
        :type event: EventData
        :return:
        """
        event.model.reset()


class CreateUserState(BaseState):

    def __init__(self, on_enter_msg, on_exit_msg):
        super().__init__(name=CREATEUSER_STATE_NAME, on_enter=[self._ask_for_info], on_exit=[self._exit_state])
        self._text_on_enter = on_enter_msg
        self._text_on_exit = on_exit_msg

    def handle(self, event):
        """
        Retrive all information needed
        Save to user model

        :param event:
        :type event: EventData
        :return:
        """

        user_model: BasicUserModel = event.kwargs["user_model"]
        request: BasicMessage = event.kwargs["request"]
        response: list = event.kwargs["response"]

        if request.payload.evidence:
            for evidence in request.payload.evidence:  # type: BasicMessage.Evidence
                user_model.add_user_info(id=evidence.id, choice_id=evidence.choice_id)

            if user_model.should_stop_sign_up():
                self.change_state = True
                user_model.set_sex_and_age()
            else:
                response.append(self.create_block_msg(payload=user_model.get_new_profile_questions()))

    def _ask_for_info(self, event: EventData):
        user_model: BasicUserModel = event.kwargs["user_model"]
        response: list = event.kwargs["response"]

        response.append(self.create_block_msg(payload=user_model.get_new_profile_questions()))


# class RiskFactorState(BaseState):
#     """
#
#     """
#
#     def __init__(self, on_enter_msg, on_exit_msg):
#         super().__init__(name=RISKFACTOR_STATE_NAME, on_enter=[self._ask_for_risk_factor],
#                          on_exit=[self._no_more_risk_factors])
#         self._text_on_enter = on_enter_msg
#         self._text_on_exit = on_exit_msg
#
#     def handle(self, event: EventData):
#
#         user_model: BasicUserModel = event.kwargs["user_model"]
#         request: BasicMessage = event.kwargs["request"]
#         response: list = event.kwargs["response"]
#
#         if request.payload.evidence:
#             for evidence in request.payload.evidence:  # type: BasicMessage.Evidence
#                 user_model.add_evidence(id=evidence.id, choice_id=evidence.choice_id)
#
#             self.change_state = True
#
#     def _ask_for_risk_factor(self, event):
#         """
#         Pick some risk factor and show to user
#         :param event:
#         :type event:EventData
#         :return:
#         """
#         user_model: BasicUserModel = event.kwargs["user_model"]
#         response: list = event.kwargs["response"]
#
#         text = "Me gustaría conocer algunos factores de riesgo"
#         response.append(self.create_text_msg(text=text))
#
#         risk_factor_list = user_model.call_risk_factor()
#
#         # Get N_RISK_FACTORS serious factors
#         serious_risk_factors = [risk for risk in risk_factor_list if risk["seriousness"] == "serious"][:N_RISk_FACTORS]
#         response.append(self.create_risf_factor_msg(payload=serious_risk_factors))
#
#     def _no_more_risk_factors(self, event):
#         response: list = event.kwargs["response"]
#         text = " Entendido! Ahora me gustaría conocer tus síntomas "
#         response.append(self.create_text_msg(text=text))


class DiagnosisState(BaseState):
    """

    """

    def __init__(self, on_enter_msg, on_exit_msg):
        super().__init__(name=DIAGNOSIS_STATE_NAME, on_enter=[self._start_interview], on_exit=[self._exit_state])
        self._text_on_enter = on_enter_msg
        self._text_on_exit = on_exit_msg

    def handle(self, event: EventData):

        user_model: BasicUserModel = event.kwargs["user_model"]
        request: BasicMessage = event.kwargs["request"]
        response: list = event.kwargs["response"]

        if request.payload.evidence:
            for evidence in request.payload.evidence:  # type: BasicMessage.Evidence
                user_model.add_evidence(id=evidence.id, choice_id=evidence.choice_id)

            user_model.call_diagnosis()
            if user_model.should_stop_diagnosis():
                self.change_state = True
            else:
                response.append(self.create_block_msg(payload=user_model.get_new_diagnosis_questions()))

    def _start_interview(self, event):
        """
        Send first round of questions
        :param event:
        :type event:EventData
        :return:
        """
        user_model: BasicUserModel = event.kwargs["user_model"]
        response: list = event.kwargs["response"]
        request: BasicMessage = event.kwargs["request"]

        for text in self._text_on_enter:
            response.append(self.create_text_msg(text=text.format(request.user_id)))

        user_model.call_diagnosis()
        response.append(self.create_block_msg(payload=user_model.get_new_diagnosis_questions()))


class TriageState(BaseState):

    def __init__(self, on_enter_msg, on_exit_msg):
        super().__init__(name=TRIAGE_STATE_NAME, on_enter=[self._show_triage_results], on_exit=[])
        self._text_on_enter = on_enter_msg
        self._text_on_exit = on_exit_msg

    def handle(self, event: EventData):
        """
        Just go back to Init. Can be extended to ask user for new actions
        :param event:
        :return:
        """
        self.change_state = True

    def _show_triage_results(self, event: EventData):
        response: list = event.kwargs["response"]
        user_model: BasicUserModel = event.kwargs["user_model"]

        user_model.call_triage()
        response.append(self.create_triage_msg(payload=user_model.get_triage()))
