import requests
from consts import *
from quiz_jsons import Quiz


class DataLoader:
    _token = open("stepik_api/temp_token").read()
    _user_headers = {'Authorization': 'Bearer {}'.format(
        _token), "content-type": "application/json"}

    @classmethod
    def user_request(cls, request_url: str):
        return requests.get(request_url, headers=cls._user_headers)

    @classmethod
    def request_entity(cls, request_url: str, id: int):
        return cls.user_request(request_url.format(id)).json()

    @classmethod
    def request_entities(cls, ids, request_url, field_name):
        def prepare_ids(ids):
            return "&".join(map(lambda id: "ids[]=" + str(id), ids))

        if len(ids) == 0:
            return []
        request_url = request_url + "?" + prepare_ids(ids)
        entities = cls.user_request(request_url).json()[field_name]
        return entities

    @classmethod
    def request_course(cls, course_id: int):
        return cls.request_entity(COURSES_PK, course_id)["courses"][0]

    @classmethod
    def request_attempt(cls, attempt_id: int):
        return cls.request_entity(ATTEMPTS_PK, attempt_id)["attempts"][0]

    @classmethod
    def request_lesson(cls, unit_id: int):
        lesson = cls.request_entity(LESSONS_PK, unit_id)["lessons"][0]
        print("loaded lesson", lesson["title"])
        return lesson

    @classmethod
    def request_correct_submission(cls, step: dict) -> dict | None:
        correct_submissions = cls.user_request(
            SUBMISSIONS + "?step={}&status=correct".format(step["id"])).json()["submissions"]
        correct_submissions = correct_submissions[0] if len(
            correct_submissions) > 0 else None
        return correct_submissions

    @classmethod
    def filter_supported_steps(cls, steps: list[dict]) -> list[dict]:
        def step_is_quiz(step: dict):
            return step["block"]["name"] in SUPPORTED_TYPES
        return list(filter(step_is_quiz, steps))

    @classmethod
    def load_course_steps(cls, course_id: int) -> list[dict]:
        course = cls.request_course(course_id)
        print('begin load course "{}"'.format(course["title"]))

        return [step
                for section in cls.request_entities(course["sections"], SECTIONS, "sections")[0:1]
                for unit in cls.request_entities(section["units"], UNITS, "units")[0:1]
                for step in cls.request_entities(cls.request_lesson(unit["lesson"])["steps"], STEPS, "steps")]

    @classmethod
    def load_quizes(cls, course_id) -> list[Quiz]:
        steps = cls.load_course_steps(course_id)
        steps = cls.filter_supported_steps(steps)
        quizes = []
        for step in steps:
            sub = cls.request_correct_submission(step)
            if (sub == None):
                continue
            attempt = cls.request_attempt(sub["attempt"])
            quizes.append(Quiz(step, sub, attempt))
        return quizes
