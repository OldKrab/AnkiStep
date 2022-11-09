from stepik_api.quiz_jsons import Quiz
from stepik_api import consts
from anki_connect_module.anki_connect_sender import AnkiConnectorSender

HARD_DECK = "duck"

def convert_simple(quiz):
    question = quiz.step["block"]["text"] 
    answer = quiz.answer[quiz.type]
    return question, answer

def choice_formatter(quiz: Quiz):
    if quiz.attempt['dataset'][consts.MULT_CHOICE_FIELD]:
        quest = "Выберите несколько вариантов из списка"
    else: 
        quest = "Выберите один вариант из списка"
    #doto this
    
def convert_choice(quiz: Quiz):
    options, answer = choice_formatter(quiz)
    question = quiz.step["block"]["text"] + '\n' + options 
    answer = quiz.answer[quiz.type]
    return question, answer

converters = {
    consts.TYPE_NUMBER: convert_simple,
    consts.TYPE_STRING: convert_simple,
    consts.TYPE_CHOICE: convert_choice,
}

# convert step into anki with types
# return map with structure as a note
def convert(quiz):
    question, answer = converters[quiz.type]
    return {
        "deckName": HARD_DECK,
        "modelName": "Basic",
        "fields": {"Front": question, "Back": answer},
    }
