from transitions import Machine, EventData
from itriage.models import BasicUserModel
from itriage.states import InitState, CreateUserState, DiagnosisState, TriageState
from itriage.utils import API_VERSION_COVID, API_MODEL_SPANISH_LA, template_chat_dict, INIT_STATE_NAME, \
    CREATEUSER_STATE_NAME, DIAGNOSIS_STATE_NAME, TRIAGE_STATE_NAME


class BaseInterview(Machine):
    """
    Finite State Machine to control interview flow

    """

    def __init__(self, states, initial_state):
        # To store response from model to user.
        self.cache_response = []

        Machine.__init__(self, states=states, initial=initial_state, ignore_invalid_triggers=False,
                         send_event=True, auto_transitions=False)
        self.add_ordered_transitions(conditions=[self.static_check_new_state],
                                     prepare=[self.static_handle])

    def handle_message(self, request):
        """
        Send a trigger to actual state to handle income message.
        Process request and generate a list of response.
        Each response is encapsulate as a Basic Message

        All params sent in next_state() will be encapsulated in a EventData object.
        Check it in transitions.core

        :param request:
        :type request: messages
        :return: a list of responses
        """

        self.cache_response = []
        self.next_state(request=request, user_model=self.user_model, response=self.cache_response)
        return self.cache_response

    @staticmethod
    def static_handle(event):
        """
        Wrapper to call handle method in each state. Override it
        Handle request send by user

        :param event:
        :type event: EventData
        :return:
        """
        event.state.handle(event)

    @staticmethod
    def static_check_new_state(event):
        """

        :param event:
        :type event: EventData
        :return:
        """
        return event.state.change_state

    def reset(self):
        self.user_model.reset_model()
        for key, value in self.states.items():
            value.reset_data()


class Covid(BaseInterview):
    """
    """

    def __init__(self, infermedica_app_id, infermedica_app_key, disable_groups=False,
                 template_chat=template_chat_dict):
        _states = [
            InitState(on_enter_msg=template_chat[INIT_STATE_NAME]["on_enter"],
                      on_exit_msg=template_chat[INIT_STATE_NAME]["on_exit"]),
            CreateUserState(on_enter_msg=template_chat[CREATEUSER_STATE_NAME]["on_enter"],
                            on_exit_msg=template_chat[CREATEUSER_STATE_NAME]["on_exit"]),
            DiagnosisState(on_enter_msg=template_chat[DIAGNOSIS_STATE_NAME]["on_enter"],
                           on_exit_msg=template_chat[DIAGNOSIS_STATE_NAME]["on_exit"]),
            TriageState(on_enter_msg=template_chat[TRIAGE_STATE_NAME]["on_enter"],
                        on_exit_msg=template_chat[TRIAGE_STATE_NAME]["on_exit"])
        ]

        self.user_model = BasicUserModel(api_model=API_MODEL_SPANISH_LA, api_version=API_VERSION_COVID,
                                         app_id=infermedica_app_id,
                                         app_key=infermedica_app_key, disable_groups=disable_groups)

        BaseInterview.__init__(self, states=_states, initial_state=INIT_STATE_NAME)
