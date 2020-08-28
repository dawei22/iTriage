from examples.commands import make_single_question, make_group_multiple_question, make_group_single_question, \
    hello, read_input
from itriage import Covid
from itriage.messages import Types, TypesQuestion, BasicMessage

if __name__ == "__main__":
    interview_engine = Covid(infermedica_app_id="XX",
                             infermedica_app_key="XX")

    print("Saluda a Doctor Us (hola)")

    if hello():
        # Parse to Basic Message
        request = BasicMessage(user_id="XX", _type=Types.TEXT)

        while True:
            response = interview_engine.handle_message(request=request)
            if response:
                request = BasicMessage(user_id="XX", _type=Types.BLOCK)

                for r in response:  # type: BasicMessage
                    if r.type == Types.TEXT:
                        print(r.text)

                    elif r.type == Types.BLOCK:
                        if isinstance(r.payload.question, BasicMessage.Question):
                            question = r.payload.question

                            if question.type == TypesQuestion.SINGLE:
                                choice_id = make_single_question(_id=question.items[0]["id"], _text=question.text,
                                                                 _choices=question.items[0]["choices"])
                                request.add_answer(_id=question.items[0]["id"], choice_id=choice_id)

                            elif question.type == TypesQuestion.GROUP_SINGLE:
                                print(question.text)
                                key, value = make_group_single_question(question.items)
                                request.add_answer(_id=key, choice_id=value)

                            elif question.type == TypesQuestion.GROUP_MULTIPLE:
                                print(question.text)
                                answers_list = make_group_multiple_question(_items=question.items)
                                for answer in answers_list:
                                    request.add_answer(_id=answer[0], choice_id=answer[1])

                        elif isinstance(r.payload.triage, BasicMessage.TriageResults):
                            triage_results = r.payload.triage
                            print(triage_results.description)
                            print(triage_results.label)
                            for s in triage_results.serious:
                                print(s)
                            break
            else:
                user_input = read_input()
                request = BasicMessage(user_id="XX", _type=Types.TEXT, text=user_input)
