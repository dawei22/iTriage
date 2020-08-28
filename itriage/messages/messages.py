import enum


class Types(enum.Enum):
    TEXT = "text"
    BLOCK = "block"


class TypesQuestion(enum.Enum):
    SINGLE = "single"
    GROUP_SINGLE = "group_single"
    GROUP_MULTIPLE = "group_multiple"


class BasicMessage:
    """
    Message to communicate with user. Send info, questions, results and retrieve new evidence
    """

    def __init__(self, user_id, _type, text: str = ""):
        self.user_id = user_id
        self.type = _type
        self.text = text
        self.payload = self.Payload()

    def add_risk_factor(self, _id, _name, _question):
        self.payload.question = self.RiskFactor(_id=_id, name=_name, question=_question)

    def add_question(self, _type, _text=None, _items=None):
        self.payload.question = self.Question(_type=_type, text=_text, items=_items)

    def add_answer(self, _id, choice_id):
        self.payload.evidence.append(self.Evidence(_id=_id, choice_id=choice_id))

    def add_triage(self, description, label, serious, triage_level):
        self.payload.triage = self.TriageResults(description=description, label=label, serious=serious,
                                                 triage_level=triage_level)

    class Payload:
        def __init__(self):
            self.question = None
            self.evidence = []
            self.triage = None

    class Question:
        def __init__(self, _type, text, items):
            self.type = _type
            self.text = text
            self.items = items

    class Evidence:
        def __init__(self, _id, choice_id):
            self.id = _id
            self.choice_id = choice_id

    class RiskFactor:
        def __init__(self, _id: str, name: str, question: str):
            self.id = _id
            self.description = name
            self.question = question

    class TriageResults:
        def __init__(self, description: str, label: str, serious: list, triage_level: str):
            self.description = description
            self.label = label
            self.serious = serious
            self.triage_level = triage_level
