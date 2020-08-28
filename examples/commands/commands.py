from examples.utils import SEX_NORM, MIN_AGE, MAX_AGE, ANSWER_NORM
from examples.utils import AmbiguousAnswerException
from examples.utils import is_hi, extract_sex, extract_age, extract_decision


def read_input(text=""):
    """
    User input can't be empty string
    :param text:
    :type text: str
    :return: user input
    """
    user_input = input(text)
    if user_input:
        return user_input
    else:
        return read_input(text)


def create_question_with_choice(text: str, choices: list):
    question_with_choice = text
    for choice in choices:
        if choice == choices[0]:
            question_with_choice += "( " + choice["label"] + ", "
        elif choice == choices[-1]:
            question_with_choice += choice["label"] + ") "
        else:
            question_with_choice += choice["label"] + ", "
    return question_with_choice


class Verifier:
    def __init__(self):
        pass

    @staticmethod
    def verify_and_filter(id, choice_id):
        if id == "sex":
            return extract_sex(choice_id, mapping=SEX_NORM)
        elif id == "age":
            age = int(extract_age(choice_id))
            if age < MIN_AGE:
                raise ValueError("Edades menores a 12 años no se pueden analizar. ")
            elif age > MAX_AGE:
                raise ValueError("La máxima edad posible de analizar es 130 años. ")
            return age
        else:
            return extract_decision(text=choice_id, mapping=ANSWER_NORM)

    @staticmethod
    def verify_mutually_exclusive_question(choice_id, options):
        if choice_id in options:
            return extract_decision(text="si", mapping=ANSWER_NORM)
        else:
            raise AmbiguousAnswerException


def hello():
    user_input = read_input()
    if is_hi(user_input):
        return True
    else:
        return hello()


def make_single_question(_id: str, _text: str, _choices: list):
    while True:
        _choice_id = read_input(create_question_with_choice(text=_text, choices=_choices))
        try:
            return Verifier.verify_and_filter(id=_id,
                                              choice_id=_choice_id)
        except AmbiguousAnswerException:
            print("No entendí")
        except ValueError as e:
            print(str(e))


def make_group_single_question(_items: list):
    mapping_idx_to_question = {}
    for idx, item in enumerate(_items, start=1):
        mapping_idx_to_question[str(idx)] = item["id"]
        print(str(idx) + " : " + item["name"])
    while True:
        _choice_id = read_input("Indica el número del síntoma que tengas ")

        try:
            return mapping_idx_to_question[_choice_id], Verifier.verify_mutually_exclusive_question(
                choice_id=_choice_id, options=mapping_idx_to_question)
        except (KeyError, AmbiguousAnswerException):
            print("Esa alternativa no está disponible ")


def make_group_multiple_question(_items: list):
    """
    Make question with multiple choices. Show one at a time. In a powerful GUI you can
    show all at once
    :param _items:
    :return: A list of (id, choice)
    """
    _evidence_list = []
    for item in _items:
        _evidence_list.append(
            [item["id"], make_single_question(_id="decision", _text=item["name"], _choices=item["choices"])])
    return _evidence_list
