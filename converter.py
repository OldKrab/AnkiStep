from stepik_api.quiz_jsons import Quiz
from stepik_api import consts
from anki_connect_module.anki_connect_sender import AnkiConnectorSender

converters = {
    consts.TYPE_NUMBER: convert_number,
    consts.TYPE_STRING: convert_string,
    consts.TYPE_CHOICE: convert_choice,
}

HARD_DECK = "duck"
def convert_number(quiz):
    question = quiz.step["block"]["text"] 
    answer = quiz.answer["number"]
    return {
        "deckName": HARD_DECK,
        "modelName": "Basic",
        "fields": {"Front": question, "Back": answer},
    }

def convert_string(quiz):
    question = quiz.step["block"]["text"] 
    answer = quiz.answer["string"]
    return {
        "deckName": HARD_DECK,
        "modelName": "Basic",
        "fields": {"Front": question, "Back": answer},
    }

# convert all steps into anki with types
# return map with structure as a notes
def convert_all(quizzes: Quiz):
    notes = {}
    for q in quizzes:
        notes.pop(converters[q.type](q))
    return
