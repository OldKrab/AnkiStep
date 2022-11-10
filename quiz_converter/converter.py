from stepik_api.quiz_jsons import Quiz
from stepik_api.consts import *
from anki_connect_module.anki_connect_sender import AnkiConnectorSender

def convert_simple_answer(quiz, type):
    question = quiz.step["block"]["text"] 
    answer = quiz.answer[type]
    return question, answer

def convert_number(quiz):
    return convert_simple_answer(quiz, "number")

def convert_string(quiz):
    return convert_simple_answer(quiz, "text")

def convert_math(quiz):
    question = quiz.step["block"]["text"] 
    answer = "<anki-mathjax>" + quiz.answer["formula"] + "</anki-mathjax>"
    return question, answer

def choice_formatter(dataset, result):
    if dataset['is_multiple_choice']:
        options = "Выберите несколько вариантов из списка: "
    else: 
        options = "Выберите один вариант из списка: "
        options += "<p>"
    for i in range(len(dataset['options'])):
        options += "<p>" + str(i + 1) + ". " + dataset['options'][i]
    answer = ""
    for i in range(len(result)) :
        if result[i]:
            answer += "<p>" + str(i + 1) + ". " + dataset['options'][i]
    return options, answer
    
def convert_choice(quiz: Quiz):
    options, answer = choice_formatter(quiz.attempt['dataset'], quiz.answer['choices'])
    question = quiz.step["block"]["text"] + '\n' + options 
    return question, answer

converters = {
    TYPE_NUMBER: convert_number,
    TYPE_STRING: convert_string,
    TYPE_CHOICE: convert_choice,
    TYPE_MATH: convert_math
}

# convert step into anki with types
# return map with structure as a note
def convert(quiz: Quiz):
    question, answer = converters[quiz.type](quiz)
    deck_name = quiz.course_name + '::' + quiz.lesson_name + '::' + quiz.section_name
    return {
        "deckName": deck_name,
        "modelName": "Basic",
        "fields": {"Front": question, "Back": answer},
        "options": {
                "allowDuplicate": False,
                "duplicateScope": "deck",
                "duplicateScopeOptions": {
                    "deckName": deck_name,
                    "checkChildren": False,
                    "checkAllModels": False
                }
            }
    }

