
from re import sub


class Quiz:
    def __init__(self, step: dict, submission: dict, attempt: dict) -> None:
        self.step = step
        self.submission = submission
        self.attempt = attempt
