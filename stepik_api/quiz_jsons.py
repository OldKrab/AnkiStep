
from re import sub


class Quiz:
    def __init__(self, step: dict, submission: dict, attempt: dict, course_name:str, section_name:str, lesson_name:str) -> None:
        self.step = step
        self.submission = submission
        self.attempt = attempt
        self.type = step['block']['name']
        self.options = step['block']['options']
        self.answer = submission['reply']
        self.course_name = course_name
        self.section_name = section_name
        self.lesson_name = lesson_name
