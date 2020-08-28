import json
from flask import Flask, request, make_response
from commands import send_msg
from interview_thread import InterviewThread, WrapperMessage
from utils import SLACK_VERIFICATION_TOKEN, random_phrases
from itriage.messages import BasicMessage, Types
from itriage.utils import logger
import re
import random

# Flask webserver for incoming traffic from Slack
app = Flask(__name__)

# Store user's channels and thread
active_users = {}


# Helper for verifying that requests came from Slack
def verify_slack_token(request_token):
    if SLACK_VERIFICATION_TOKEN != request_token:
        logger.error("Error: invalid verification token!")
        logger.error("Received {} but was expecting {}".format(request_token, SLACK_VERIFICATION_TOKEN))
    else:
        return True


@app.route("/slack/triage", methods=["POST"])
def start_triage():
    """
    The endpoint Slack will start a new triage when recive "/triage" command.
    If user already exist, restart it
    :return:
    """
    if verify_slack_token(request_token=request.form["token"]):
        if "command" in request.form and request.form["command"] == "/triage":
            channel_id = request.form["channel_id"]
            user_id = request.form["user_id"]

            if user_id in active_users:
                try:
                    active_users[user_id].stop_run()
                    # TODO: Puede que no sea necesario, al llamar el metodo de arriba ya se detiene
                    active_users[user_id].join()
                    logger.debug("Old thread {0} removed".format(user_id))
                except Exception as e:
                    logger.error(str(e))

            active_users[user_id] = InterviewThread(name="Thread {0}".format(user_id), user_id=user_id,
                                                    channel_id=channel_id)

            # trigger to start CovidInterview FSM
            trigger_to_interview = WrapperMessage(
                basic_message=BasicMessage(user_id=user_id, _type=Types.TEXT, text="hola"))
            active_users[user_id].add_new_msg(trigger_to_interview)

            try:
                logger.debug("Starting Thread {0}".format(user_id))
                active_users[user_id].start()
            except Exception as e:
                logger.critical(str(e))
        return make_response("", 200)
    else:
        return make_response("Request contains invalid Slack verification token", 403)


@app.route("/slack/message_actions", methods=["POST"])
def message_actions():
    """
    The endpoint Slack will get the user's actions
    Act as a broker
    :return:
    """
    # TODO: Manejar caso en que se aprietan botones ya procesados
    # Parse the request payload
    form_json = json.loads(request.form["payload"])

    # Verify that the request came from Slack
    if verify_slack_token(form_json["token"]):

        if form_json["type"] == "block_actions":

            if form_json["actions"][0]["type"] == "static_select":
                # Parse to BasicMessage
                new_request = BasicMessage(user_id=form_json["user"]["id"], _type=Types.BLOCK)
                new_request.add_answer(_id=form_json["actions"][0]["block_id"],
                                       choice_id=form_json["actions"][0]["selected_option"]["value"])

            elif form_json["actions"][0]["type"] == "button":
                view = active_users[form_json["user"]["id"]].get_modal_waiting()
                active_users[form_json["user"]["id"]].slack_client.views_open(trigger_id=form_json["trigger_id"],
                                                                              view=view)
                return make_response("", 200)

        elif form_json["type"] == "view_submission":
            new_request = BasicMessage(user_id=form_json["user"]["id"], _type=Types.BLOCK)

            for id, choice in form_json["view"]["state"]["values"].items():
                if re.match("radio_button", id):
                    new_request.add_answer(_id=choice["action_id"]["selected_option"]["value"], choice_id="present")
                elif re.match("select", id):
                    action_id = id.split(" ")[1]
                    new_request.add_answer(_id=action_id, choice_id=choice[action_id]["selected_option"]["value"])

            # Send random message to show spontaneity
            send_msg(slack_client=active_users[form_json["user"]["id"]].slack_client,
                     channel=active_users[form_json["user"]["id"]].channel_id,
                     logger=logger, text=random.choice(random_phrases))

        income_msg = WrapperMessage(basic_message=new_request)

        # Add to queue
        active_users[form_json["user"]["id"]].add_new_msg(income_msg)

        # Send an HTTP 200 response with empty body so Slack knows we're done here
        return make_response("", 200)
    else:
        return make_response("Request contains invalid Slack verification token", 403)


# Start the Flask server
if __name__ == "__main__":
    # ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
    app.run("localhost", 5000)
