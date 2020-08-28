import threading
import time

from slack import WebClient
from utils import SLACK_BOT_TOKEN
from commands import send_msg, make_single_question, make_group_multiple_question, \
    make_group_single_question, display_triage_results
from itriage import Covid
from itriage.messages import BasicMessage, TypesQuestion, Types
from itriage.utils import INFERMEDICA_APP_KEY, INFERMEDICA_APP_ID, logger

import time


class WrapperMessage:
    """
    Encapsulated Basic Message in case we need to handle more info. Add attributes in case you need to handle more
    info than Basic Message
    eg.
        self.ts = timestamp that was created
    """

    def __init__(self, basic_message):
        self.basic_message = basic_message


class InterviewThread(threading.Thread):
    def __init__(self, name, user_id, channel_id):
        super().__init__()
        self.name = name
        self.user_id = user_id
        self.channel_id = channel_id
        self.slack_client = WebClient(token=SLACK_BOT_TOKEN, timeout=5)

        self.interview_engine = Covid(infermedica_app_id=INFERMEDICA_APP_ID,
                                      infermedica_app_key=INFERMEDICA_APP_KEY)

        self.queue_in = []
        self._stop = False

        self.modals = []

    def run(self):
        while not self._stop:
            if self.queue_in:  # type: list
                income_msg: WrapperMessage = self.queue_in.pop()
                _request: BasicMessage = income_msg.basic_message

                logger.debug("Processing new message...")
                try:
                    _begin_time = time.time()
                    responses = self.interview_engine.handle_message(request=_request)
                    logger.info("Time FSM : ", time.time() - _begin_time)

                except Exception as e:
                    logger.critical(str(e))
                else:
                    logger.debug("Message processed !")
                    if responses:
                        _begin_time = time.time()
                        self.send_response(responses)
                        logger.info("Time response : ", time.time() - _begin_time)
            time.sleep(0.5)

    def send_response(self, responses):
        for response in responses:  # type: BasicMessage
            if response.type == Types.TEXT:
                send_msg(slack_client=self.slack_client, channel=self.channel_id,
                         text=response.text,
                         logger=logger)

            elif response.type == Types.BLOCK:
                if isinstance(response.payload.question, BasicMessage.Question):
                    question = response.payload.question

                    if question.type == TypesQuestion.SINGLE:
                        blocks = make_single_question(question)
                        send_msg(slack_client=self.slack_client, channel=self.channel_id,
                                 blocks=blocks,
                                 logger=logger)

                    elif question.type == TypesQuestion.GROUP_SINGLE:
                        blocks, view = make_group_single_question(question)
                        self.modals.append(view)
                        send_msg(slack_client=self.slack_client, channel=self.channel_id,
                                 blocks=blocks,
                                 logger=logger)

                    elif question.type == TypesQuestion.GROUP_MULTIPLE:
                        blocks, view = make_group_multiple_question(question)
                        self.modals.append(view)
                        send_msg(slack_client=self.slack_client, channel=self.channel_id,
                                 blocks=blocks,
                                 logger=logger)

                elif isinstance(response.payload.triage, BasicMessage.TriageResults):
                    blocks = display_triage_results(response.payload.triage)
                    send_msg(slack_client=self.slack_client, channel=self.channel_id,
                             blocks=blocks,
                             logger=logger)
                    self._stop = True

    def add_new_msg(self, new_msg):
        self.queue_in.append(new_msg)

    def get_modal_waiting(self):
        return self.modals.pop()

    def stop_run(self):
        self._stop = True
