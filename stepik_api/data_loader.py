from __future__ import annotations

from html import entities
import multiprocessing
import requests
from stepik_api.authorisation import OAuthStepik
from stepik_api.consts import *
from stepik_api.quiz_jsons import Quiz
from joblib import Parallel, delayed


def user_request(user_headers, request_url: str):
    return requests.get(request_url, headers=user_headers)


def request_entity(user_headers, request_url: str, id: int):
    return user_request(user_headers, request_url.format(id)).json()


def parse_url_params(params: dict) -> str:
    return "?" + "&".join(map(lambda pair: "{}={}".format(pair[0], pair[1]), params.items()))


def request_entities(user_headers, request_url, url_params: dict, field_name) -> list[dict]:
    left_pages = True
    entities = []
    page = 1
    while left_pages:
        url_params["page"] = page
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
    return request_entity(user_headers, COURSES_PK, course_id)["courses"][0]


def request_attempt(user_headers, attempt_id: int):
    return request_entity(user_headers, ATTEMPTS_PK, attempt_id)["attempts"][0]


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
    print("loaded sections of course")
    return sections


def load_course_units(user_headers, course_id: int) -> list[dict]:
    units = request_entities(user_headers, UNITS, {
                             "course": course_id}, "units")
    print("loaded units of course")
    return units


def load_course_lessons(user_headers, course_id: int) -> list[dict]:
    lessons = request_entities(user_headers,
                               LESSONS, {"course": course_id}, "lessons")
    print("loaded lessons of course")

    return lessons


def load_course(user_headers, course_id: int) -> dict:
    course = request_course(user_headers, course_id)
    print('loaded course with id {}'.format(course_id))
    return course


def load_lessons_steps(user_headers, lessons: list[dict]) -> list[dict]:
    steps_ids = [
        step_id for lesson in lessons for step_id in lesson["steps"]]
    steps = request_entities_by_ids(user_headers, steps_ids, STEPS, "steps")
    print("loaded steps of lessons")
    return steps


def load_step_submission_and_attempt(user_headers, steps, i, course, steps_lessons, steps_sections):
    step_id = steps[i]["id"]
    sub = request_correct_submission(user_headers, step_id)
    if (sub == None):
        return None
    attempt = request_attempt(user_headers, sub["attempt"])

    print("loaded submission and attempt for {}'th step in lesson \"{}\"".format(
        steps[i]["position"], steps_lessons[i]["title"]))

    return Quiz(
        steps[i], sub, attempt, course["title"], steps_lessons[i]["title"], steps_sections[i]["title"])


def load_quizes(user_headers, course_id) -> list[Quiz]:
    num_cores = multiprocessing.cpu_count()
    course = load_course(user_headers, course_id)

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

    quizes = Parallel(n_jobs=min(50, len(steps)))(
        delayed(load_step_submission_and_attempt)(
            user_headers, steps, i, course, steps_lessons, steps_sections)
        for i in range(len(steps)))

    quizes = filter(lambda o: o is not None, quizes)
    return list(quizes)
