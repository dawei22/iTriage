from slack.errors import SlackApiError
from itriage.messages import BasicMessage


def send_msg(slack_client, channel, logger, text=None, blocks=None):
    try:
        slack_client.chat_postMessage(channel=channel, text=text, blocks=blocks)
        logger.debug("Response sent")
    except SlackApiError as e:
        logger.error(str(e))


def make_single_question(question: BasicMessage.Question):
    blocks = [
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": question.text
            },
            "block_id": question.items[0]["id"],
            "accessory": {
                "type": "static_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Selecciona una respuesta",
                    "emoji": True
                },
                "options": []
            },
        }
    ]
    if question.items[0]["id"] == "age":
        for i in range(12, 111):
            age_option = {
                "text": {
                    "type": "plain_text",
                    "text": str(i),
                    "emoji": True
                },
                "value": str(i)
            }
            blocks[1]["accessory"]["options"].append(age_option)
    else:
        for choice in question.items[0]["choices"]:
            age_option = {
                "text": {
                    "type": "plain_text",
                    "text": choice["label"],
                    "emoji": True
                },
                "value": choice["id"]
            }
            blocks[1]["accessory"]["options"].append(age_option)

    return blocks


def make_group_single_question(question: BasicMessage.Question):
    blocks = [
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": question.text
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Seleccionar",
                    "emoji": True
                },
                "value": "Show",
                "style": "primary"
            }
        }
    ]

    view = {
        "type": "modal",
        "title": {
            "type": "plain_text",
            "text": "DoctorUs",
            "emoji": True
        },
        "submit": {
            "type": "plain_text",
            "text": "OK",
            "emoji": True
        },
        "close": {
            "type": "plain_text",
            "text": "Volver",
            "emoji": True
        },
        "blocks": [
            {
                "type": "divider"
            },
            {
                "type": "input",
                "block_id": "radio_button",
                "label": {
                    "type": "plain_text",
                    "text": question.text,
                    "emoji": True
                },
                "element": {
                    "type": "radio_buttons",
                    "action_id": "action_id",
                    "options": []
                }
            }
        ]
    }

    for item in question.items:
        radio_button = {
            "text": {
                "type": "plain_text",
                "text": item["name"]
            },
            "value": item["id"],
        }
        view["blocks"][1]["element"]["options"].append(radio_button)

    return blocks, view


def make_group_multiple_question(question: BasicMessage.Question):
    blocks = [
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": question.text
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Seleccionar",
                    "emoji": True
                },
                "value": "Show",
                "style": "primary"
            }
        }
    ]

    view = {
        "type": "modal",
        "title": {
            "type": "plain_text",
            "text": "DoctorUs",
            "emoji": True
        },
        "submit": {
            "type": "plain_text",
            "text": "OK",
            "emoji": True
        },
        "close": {
            "type": "plain_text",
            "text": "Volver",
            "emoji": True
        },
        "blocks": [
            {
                "type": "divider"
            },
        ]
    }
    for item in question.items:
        select = {
            "type": "input",
            "block_id": "select " + item["id"],
            "element": {
                "type": "static_select",
                "action_id": item["id"],
                "placeholder": {
                    "type": "plain_text",
                    "text": "Selecciona una respuesta",
                    "emoji": True
                },
                "options": []
            },
            "label": {
                "type": "plain_text",
                "text": item["name"],
                "emoji": True
            }
        }

        for choice in item["choices"]:
            option = {
                "text": {
                    "type": "plain_text",
                    "text": choice["label"],
                    "emoji": True
                },
                "value": choice["id"]
            }
            select["element"]["options"].append(option)
        view["blocks"].append(select)

    return blocks, view


def display_triage_results(triage: BasicMessage.TriageResults):
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": ":crystal_ball:  *Resultados del Triage*  :crystal_ball:"
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": " :loud_sound: *{0}* :loud_sound:".format(triage.label),
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": triage.description
            }
        }
    ]

    if triage.serious:
        serious_context = [
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Nivel de seriedad de síntomas*"
                }
            },
        ]
        blocks = blocks + serious_context

        obs_emergency = ""
        obs_no_emergency = ""

        for obs in triage.serious:
            if obs["is_emergency"]:
                obs_emergency += obs["common_name"] + " \n\n"
            else:
                obs_no_emergency += obs["common_name"] + " \n\n"

        if obs_emergency != "":
            block_emergency = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": ":ambulance: *Urgentes!* "
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": obs_emergency
                    }
                },
            ]
            blocks = blocks + block_emergency

        elif obs_no_emergency != "":
            block_no_emergency = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": ":pill: *Peligrosos*"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": obs_no_emergency
                    }
                },
            ]

            blocks = blocks + block_no_emergency
    final_block = [
        {
            "type": "divider"
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": ":hospital: Minsal"
                }
            ]
        }
    ]

    return blocks + final_block
