from stepik_api.quiz_jsons import Quiz
from stepik_api.consts import *
from anki_connect_module.anki_connect_sender import AnkiConnectorSender
from sympy import core, latex


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
    answer = "[$]" + latex(core.sympify(quiz.answer["formula"], evaluate=False))  + "[/$]"
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
    question = quiz.step["block"]["text"] + "<br>" + options 
    return question, answer


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

    a = "<table>"
    for i in range(len(keys)):
        a += make_html_row(keys[i], values[answer[i]])
    a += "</table>"

    return q, a

def convert_sorting(quiz: Quiz):
    q = quiz.step["block"]["text"] + '\n'

    q += "<br><strong> Отсортируйте строки: </strong>"
    q += "<table>"

    values = []
    for pair in quiz.attempt['dataset']['options']:
        values.append(pair)
        q += F"<tr>  <td>{pair}</td>  </tr>"
    q += "</table>"

    answer = quiz.answer['ordering']

    a = "<table>"
    for i in range(len(values)):
        a += F"<tr>  <td>{values[answer[i]]}</td>  </tr>"
    a += "</table>"

    return q, a


def convert_random(quiz: Quiz):
    question = quiz.step["block"]["text"] + " " + quiz.attempt['dataset']['task']
    return question, quiz.answer["answer"]

def make_select_html(question: dict, keys: dict):
    res = question['text'] + ' '
    res += "<select>"
    for key in keys['options']:
        res += F"<option> {key} </option>"
    res += '</select>'
    return res


def convert_fill_blanks(quiz: Quiz):
    question = quiz.step["block"]["text"] + ' \n'

    data = quiz.attempt['dataset']['components']
    for i in range(0, len(data), 2):
        question += make_select_html(data[i], data[i+1]) + '\t '

    answer = ""
    for i in range(0, len(data), 2):
        answer += data[i]['text'] + ' ' + quiz.answer["blanks"][i // 2] + '\t '

    return question, answer

def convert_free_answer(quiz: Quiz):
    question = quiz.step["block"]["text"] + ' \n'
    answer = quiz.answer['text']
    return question, answer


converters = {
    TYPE_NUMBER: convert_number,
    TYPE_STRING: convert_string,
    TYPE_CHOICE: convert_choice,
    TYPE_MATH: convert_math,
    TYPE_MATCHING: convert_matching, 
    TYPE_RANDOM_TASKS: convert_random,
    TYPE_FILL_BLANKS: convert_fill_blanks,
    TYPE_SORTING: convert_sorting,
    TYPE_FREE_ANSWER: convert_free_answer,
}


# convert step into anki with types
# return map with structure as a note
def convert(quiz: Quiz):
    question, answer = converters[quiz.type](quiz)
    question = "<center>" + question + "</center>"
    answer = "<center>" + answer + "</center>"
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
