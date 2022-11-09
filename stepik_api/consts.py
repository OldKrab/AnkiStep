STEPIK_HOST = "https://stepik.org/"
STEPIK_API_URL = STEPIK_HOST + "api"

LESSONS = STEPIK_API_URL + "/lessons/"
LESSONS_PK = LESSONS + "{}"

STEPS = STEPIK_API_URL + "/steps/"

COURSES = STEPIK_API_URL + "/courses/"
COURSES_PK = COURSES + "{}"

SECTIONS = STEPIK_API_URL + "/sections/"

UNITS = STEPIK_API_URL + "/units/"

TYPE_CHOICE = "choice"
TYPE_SORTING = "sorting"
TYPE_MATCHING = "matching"
TYPE_TABLE = "table"
TYPE_FILL_BLANKS = "fill-blanks"
TYPE_NUMBER = "number"
TYPE_MATH = "math"
TYPE_RANDOM_TASKS = "random-tasks"
TYPE_STRING = "string"
TYPE_FREE_ANSWER = "free-answer"
TYPE_CODE = "code"
TYPE_SQL = "sql"
TYPE_TEXT = "text"

SUPPORTED_TYPES = {TYPE_CHOICE, TYPE_TEXT, TYPE_NUMBER}