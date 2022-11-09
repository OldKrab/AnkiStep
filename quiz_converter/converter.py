from stepik_api.quiz_jsons import Quiz
from stepik_api.consts import *
from anki_connect_module.anki_connect_sender import AnkiConnectorSender

HARD_DECK = "duck"

def convert_simple(quiz):
    question = quiz.step["block"]["text"] 
    answer = quiz.answer[quiz.type]
    return question, answer

def choice_formatter(dataset, result):
    if dataset['is_multiple_choice']:
        options = "Выберите несколько вариантов из списка: "
    else: 
        options = "Выберите один вариант из списка: "
    for i in range(len(dataset['options'])):
        options += "\n" + str(i + 1) + dataset['options'][i]
    answer = ["\n" + str(i + 1) + "." + x for i, x in enumerate(result) if x]
    return options, answer
    
    #doto this
    
def convert_choice(quiz: Quiz):
    options, answer = choice_formatter(quiz.attempt['dataset'], quiz.answer['reply']['choices'])
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
