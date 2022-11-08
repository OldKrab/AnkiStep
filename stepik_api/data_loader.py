import requests
from consts import *


class DataLoader:
    _token = open("stepik_api/temp_token").read()
    _user_headers = {'Authorization': 'Bearer {}', "content-type": "application/json".format(_token)}

    @classmethod
    def load_course_steps(cls, course_id: int) -> list[dict]:
        def request_entity(request_url: str, id: int):
            return requests.get(request_url.format(id), headers=cls._user_headers).json()

        def request_entities(ids, request_url, field_name):
            def prepare_ids(ids):
                return "&".join(map(lambda id: "ids[]=" + str(id), ids))
            request_url = request_url + "?" + prepare_ids(ids)
            entities = requests.get(request_url, headers=cls._user_headers).json()[field_name]
            return entities

        def request_course(course_id: int):
            return request_entity(COURSES_PK, course_id)["courses"][0]

        def request_lesson(unit_id: int):
            lesson = request_entity(LESSONS_PK, unit_id)["lessons"][0]
            print("loaded lesson", lesson["title"])
            return lesson

        course = request_course(course_id)
        print('begin load course "{}"'.format(course["title"]))

        return [step
                for section in request_entities(course["sections"], SECTIONS, "sections")
                for unit in request_entities(section["units"], UNITS, "units")
                for step in request_entities(request_lesson(unit["lesson"])["steps"], STEPS, "steps")]

