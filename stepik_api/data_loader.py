from __future__ import annotations

from html import entities
import multiprocessing
import requests
from stepik_api.authorisation import OAuthStepik
from stepik_api.consts import *
from stepik_api.quiz_jsons import Quiz
from joblib import Parallel, delayed


def printProgressBar(percent, prefix='', suffix='', length=50, fill='█', printEnd="\r"):
    filledLength = int(length * percent)
    percent = ("{0:." + str(1) + "f}").format(100 * percent)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)


def user_request(user_headers, request_url: str):
    return requests.get(request_url, headers=user_headers)


def request_entity(user_headers, request_url: str, id: int, fields_name: str):
    json: dict = user_request(user_headers, request_url.format(id)).json()
    if fields_name not in json.keys():
        raise Exception()
    return json[fields_name][0]


def parse_url_params(params: dict) -> str:
    return "?" + "&".join(map(lambda pair: "{}={}".format(pair[0], pair[1]), params.items()))


def request_entities(user_headers, request_url, url_params: dict, field_name, count=-1) -> list[dict]:
    left_pages = True
    entities = []
    page = 1
    cur_count = 0
    while left_pages and (count == -1 or len(entities) <= count):
        url_params["page"] = page
        url_params["page_size"] = count - len(entities)

        json = user_request(user_headers,
                            request_url + parse_url_params(url_params)).json()
        entities += json[field_name]
        left_pages = json["meta"]["has_next"]
        page += 1
    return entities


def request_entities_by_ids(user_headers, ids, request_url, field_name):
    batch_size = 20
    entities = Parallel(n_jobs=len(ids) // batch_size + 1)(
        delayed(request_entities)(
            user_headers, request_url, {"ids[]": "&ids[]=".join(map(str, ids[i:i+batch_size]))}, field_name)
        for i in range(0, len(ids), batch_size))
    if (entities is None):
        return []
    entities = [e for ee in entities for e in ee]
    return entities


def request_course(user_headers, course_id: int):
    try:
        return request_entity(user_headers, COURSES_PK, course_id, "courses")
    except Exception:
        raise ConnectionError("Can't load course with id {}".format(course_id))


def request_attempt(user_headers, attempt_id: int):
    return request_entity(user_headers, ATTEMPTS_PK, attempt_id, "attempts")


def request_correct_submission(user_headers, step_id: int) -> dict | None:
    correct_subs = request_entities(user_headers, SUBMISSIONS,
                                    {"step": step_id, "status": "correct", "order": "desc"}, "submissions")
    correct_subs = correct_subs[0] if len(correct_subs) > 0 else None
    return correct_subs


def filter_supported_steps(steps: list[dict]) -> list[dict]:
    def step_is_quiz(step: dict):
        return step["block"]["name"] in SUPPORTED_TYPES
    return list(filter(step_is_quiz, steps))


def load_course_sections(user_headers, course: dict) -> list[dict]:
    sections = request_entities_by_ids(user_headers,
                                       course["sections"], SECTIONS, "sections")
    return sections


def load_course_units(user_headers, course_id: int) -> list[dict]:
    units = request_entities(user_headers, UNITS, {
                             "course": course_id}, "units")
    return units


def load_course_lessons(user_headers, course_id: int) -> list[dict]:
    lessons = request_entities(user_headers,
                               LESSONS, {"course": course_id}, "lessons")
    return lessons


def load_course(user_headers, course_id: int) -> dict:
    print('load course with id {}...'.format(course_id))
    course = request_course(user_headers, course_id)
    return course


def load_lessons_steps(user_headers, lessons: list[dict]) -> list[dict]:
    print("load steps of lessons...")
    steps_ids = [
        step_id for lesson in lessons for step_id in lesson["steps"]]
    steps = request_entities_by_ids(user_headers, steps_ids, STEPS, "steps")
    return steps


def load_step_submission_and_attempt(user_headers, steps, i, course, steps_lessons, steps_sections, loaded_steps_count):
    def increase_progress_bar():
        loaded_steps_count[0] += 1
        printProgressBar(loaded_steps_count[0] / len(steps),
                         prefix="load steps submissions:", suffix="Complete")

    step_id = steps[i]["id"]
    sub = request_correct_submission(user_headers, step_id)
    if (sub == None):
        increase_progress_bar()
        return None
    attempt = request_attempt(user_headers, sub["attempt"])

    increase_progress_bar()
    return Quiz(
        steps[i], sub, attempt, course["title"], steps_lessons[i]["title"], steps_sections[i]["title"])


def load_user_courses(user_headers, count = 5) -> list[dict]:
    courses = request_entities(user_headers, USER_COURSES, {}, "user-courses")
    courses_ids = [course["course"] for course in courses][0:count]
    count = len(courses_ids)
    courses = request_entities_by_ids(user_headers, courses_ids, COURSES, "courses")
    courses_index = {courses[i]["id"]:i for i in range(count)}
    return [courses[courses_index[courses_ids[i]]] for i in range(count)]

def load_quizes(user_headers, course_id) -> list[Quiz]:
    num_cores = multiprocessing.cpu_count()
    course = load_course(user_headers, course_id)

    print("load sections, units and lessons of course \"{}\"...".format(course["title"]))
    sections, units, lessons = Parallel(n_jobs=3)((
        delayed(load_course_sections)(user_headers, course),
        delayed(load_course_units)(user_headers, course_id),
        delayed(load_course_lessons)(user_headers, course_id)))  # type: ignore

    steps = load_lessons_steps(user_headers, lessons)
    steps = filter_supported_steps(steps)
    if len(steps) == 0:
        return []

    lessons_index = {lessons[i]["id"]: i for i in range(len(lessons))}
    sections_index = {sections[i]["id"]: i for i in range(len(sections))}

    lessons_units_index = [0] * len(lessons)
    for i in range(len(units)):
        lessons_units_index[lessons_index[units[i]["lesson"]]] = i

    steps_lessons_ids = [step["lesson"] for step in steps]
    steps_units_ids = [lessons_units_index[lessons_index[lesson_id]]
                       for lesson_id in steps_lessons_ids]
    steps_sections_ids = [units[i]["section"]
                          for i in steps_units_ids]
    steps_lessons = [lessons[lessons_index[lesson_id]]
                     for lesson_id in steps_lessons_ids]
    steps_sections = [sections[sections_index[sections_id]]
                      for sections_id in steps_sections_ids]

    quizes = []

    loaded_steps_count = [0]
    quizes = Parallel(n_jobs=min(50, len(steps)), require='sharedmem')(
        delayed(load_step_submission_and_attempt)(
            user_headers, steps, i, course, steps_lessons, steps_sections, loaded_steps_count)
        for i in range(len(steps)))
    print()

    quizes = filter(lambda o: o is not None, quizes)
    return list(quizes)
