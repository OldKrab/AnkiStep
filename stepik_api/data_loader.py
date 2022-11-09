from __future__ import annotations

from html import entities
import multiprocessing
import requests

from stepik_api.authorisation import OAuthStepik
from stepik_api.consts import *
from stepik_api.quiz_jsons import Quiz
from joblib import Parallel, delayed


class DataLoader:
    # _token = open('stepik_api\\temp_token').read()
    # _user_headers = {'Authorization': 'Bearer {}'.format(
    #     _token), "content-type": "application/json"}

    stepic_oauth = None

    @classmethod
    def set_loader(cls, stepic_oauth: OAuthStepik = None):
        cls.stepic_oauth = stepic_oauth

    @classmethod
    def get_user_headers(cls):
        return cls.stepic_oauth.get_headers()

    @classmethod
    def user_request(cls, request_url: str):
        return requests.get(request_url, headers=cls.get_user_headers())

    @classmethod
    def request_entity(cls, request_url: str, id: int):
        return cls.user_request(request_url.format(id)).json()

    @classmethod
    def parse_url_params(cls, params: dict) -> str:
        return "?" + "&".join(map(lambda pair: "{}={}".format(pair[0], pair[1]), params.items()))

    @classmethod
    def request_entities(cls, request_url, url_params: dict, field_name) -> list[dict]:
        left_pages = True
        entities = []
        page = 1
        while left_pages:
            url_params["page"] = page
            json = cls.user_request(
                request_url + cls.parse_url_params(url_params)).json()
            entities += json[field_name]
            left_pages = json["meta"]["has_next"]
            page += 1
        return entities

    @classmethod
    def request_entities_by_ids(cls, ids, request_url, field_name):
        entities = []
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            cur_ids = ids[i:i+batch_size]
            entities += cls.request_entities(
                request_url, {"ids[]": "&ids[]=".join(map(str, cur_ids))}, field_name)
        return entities

    @classmethod
    def request_course(cls, course_id: int):
        return cls.request_entity(COURSES_PK, course_id)["courses"][0]

    @classmethod
    def request_attempt(cls, attempt_id: int):
        return cls.request_entity(ATTEMPTS_PK, attempt_id)["attempts"][0]

    @classmethod
    def request_correct_submission(cls, step_id: int) -> dict | None:
        correct_subs = cls.request_entities(SUBMISSIONS,
                                            {"step": step_id, "status": "correct", "order": "desc"}, "submissions")
        correct_subs = correct_subs[0] if len(correct_subs) > 0 else None
        return correct_subs

    @classmethod
    def filter_supported_steps(cls, steps: list[dict]) -> list[dict]:
        def step_is_quiz(step: dict):
            return step["block"]["name"] in SUPPORTED_TYPES
        return list(filter(step_is_quiz, steps))

    @classmethod
    def load_course_sections(cls, course: dict) -> list[dict]:
        sections = cls.request_entities_by_ids(
            course["sections"], SECTIONS, "sections")
        print("loaded sections of course")
        return sections

    @classmethod
    def load_course_units(cls, course_id: int) -> list[dict]:
        units = cls.request_entities(UNITS, {"course": course_id}, "units")
        print("loaded units of course")
        return units

    @classmethod
    def load_course_lessons(cls, course_id: int) -> list[dict]:
        lessons = cls.request_entities(
            LESSONS, {"course": course_id}, "lessons")
        print("loaded lessons of course")

        return lessons

    @classmethod
    def load_course(cls, course_id: int) -> dict:
        course = cls.request_course(course_id)
        print('loaded course with id {}'.format(course_id))
        return course

    @classmethod
    def load_lessons_steps(cls, lessons: list[dict]) -> list[dict]:
        steps_ids = [
            step_id for lesson in lessons for step_id in lesson["steps"]]
        steps = cls.request_entities_by_ids(steps_ids, STEPS, "steps")
        print("loaded steps of lessons")
        return steps

    @classmethod
    def load_quizes(cls, course_id) -> list[Quiz]:
        num_cores = multiprocessing.cpu_count()
        course = cls.load_course(course_id)

        sections, units, lessons = Parallel(n_jobs=3)((
            delayed(cls.load_course_sections)(course),
            delayed(cls.load_course_units)(course_id),
            delayed(cls.load_course_lessons)(course_id)))  # type: ignore
        steps = cls.load_lessons_steps(lessons)
        steps = cls.filter_supported_steps(steps)

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

        def calc_for_step(i: int):
            step_id = steps[i]["id"]
            sub = cls.request_correct_submission(step_id)
            if (sub == None):
                return None
            attempt = cls.request_attempt(sub["attempt"])

            print("loaded submission and attempt for {}'th step in lesson \"{}\"".format(
                steps[i]["position"], steps_lessons[i]["title"]))

            return Quiz(
                steps[i], sub, attempt, course["title"], steps_lessons[i]["title"], steps_sections[i]["title"])

        quizes = Parallel(n_jobs=min(num_cores, len(steps)))(delayed(calc_for_step)(i)
                                            for i in range(len(steps)))
        quizes = filter(lambda o: o is not None, quizes)
        return list(quizes)
