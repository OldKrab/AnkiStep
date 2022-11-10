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
        options = "<br><strong>Выберите несколько вариантов из списка: </strong>"
    else:
        options = "<br><strong>Выберите один вариант из списка: </strong>"
        options += "<br>"
    for i in range(len(dataset['options'])):
        options += "<br>" + str(i + 1) + ". " + dataset['options'][i]
    answer = ""
    for i in range(len(result)):
        if result[i]:
            answer += "<br>" + str(i + 1) + ". " + dataset['options'][i]
    return options, answer


def convert_choice(quiz: Quiz):
    options, answer = choice_formatter(quiz.attempt['dataset'], quiz.answer['choices'])
    question = quiz.step["block"]["text"] + '\n' + options
    return question, answer

def convert_fill_blanks(quiz:Quiz):
    a = quiz
    return "q", "a"


def make_html_row(key, value):
    return F"<tr><td>{key}</td>  <td width = 25em> </td>  <td>{value}</td></tr>"


def convert_matching(quiz: Quiz):
    q = quiz.step["block"]["text"] + '\n'

    q += "<br><strong>Сопоставьте объекты из двух столбцов: </strong>"

    q += "<table>"

    keys = []
    values = []

    for pair in quiz.attempt['dataset']['pairs']:
        keys.append(pair['first'])
        values.append(pair['second'])
        q += make_html_row(pair['first'], pair['second'])
    q += "</table>"

    answer = quiz.answer['ordering']

    # keys = list(quiz.attempt['dataset']['pairs'].keys())
    # values = list(quiz.attempt['dataset']['pairs'].values())

    a = "<table>"
    for i in range(len(keys)):
        a += make_html_row(keys[i], values[answer[i]])
    a += "</table>"

    return q, a


converters = {
    TYPE_NUMBER: convert_number,
    TYPE_STRING: convert_string,
    TYPE_CHOICE: convert_choice,
    TYPE_MATH: convert_math,
    TYPE_FILL_BLANKS: convert_fill_blanks,
    TYPE_MATCHING: convert_matching
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
