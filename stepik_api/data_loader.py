from html import entities
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
        print("load sections of course")
        return cls.request_entities_by_ids(course["sections"], SECTIONS, "sections")

    @classmethod
    def load_course_units(cls, course_id: int) -> list[dict]:
        print("load units of course")
        units = cls.request_entities(UNITS, {"course": course_id}, "units")
        return units

    @classmethod
    def load_course_lessons(cls, course_id: int) -> list[dict]:
        print("load lessons of course")
        lessons = cls.request_entities(
            LESSONS, {"course": course_id}, "lessons")
        return lessons

    @classmethod
    def load_course(cls, course_id: int) -> dict:
        print('load course with id {}'.format(course_id))
        course = cls.request_course(course_id)
        return course

    @classmethod
    def load_lessons_steps(cls, lessons: list[dict]) -> list[dict]:
        print("load steps of lessons")
        steps_ids = [
            step_id for lesson in lessons for step_id in lesson["steps"]]
        steps = cls.request_entities_by_ids(steps_ids, STEPS, "steps")
        return steps

    @classmethod
    def load_quizes(cls, course_id) -> list[Quiz]:
        course = cls.load_course(course_id)
        sections = cls.load_course_sections(course)
        units = cls.load_course_units(course_id)
        lessons = cls.load_course_lessons(course_id)
        steps = cls.load_lessons_steps(lessons)
        steps = cls.filter_supported_steps(steps)

        lessons_index = {lessons[i]["id"]: i for i in range(len(lessons))}
        sections_index = {sections[i]["id"]: i for i in range(len(sections))}
        units_index = {units[i]["id"]: i for i in range(len(units))}
        steps_index = {steps[i]["id"]: i for i in range(len(steps))}

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
        for i in range(len(steps)):
            step_id = steps[i]["id"]

            print("load submission and attempt for {}'th step in lesson \"{}\"".format(
                steps[i]["position"], steps_lessons[i]["title"]))

            sub = cls.request_correct_submission(step_id)
            if (sub == None):
                continue
            attempt = cls.request_attempt(sub["attempt"])
            quizes.append(Quiz(
                steps[i], sub, attempt, course["title"], steps_lessons[i]["title"], steps_sections[i]["title"]))
        return quizes
