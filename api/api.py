
from anki_connect_module.anki_connect_sender import AnkiConnectorSender
from quiz_converter.converter import convert
from stepik_api.authorisation import OAuthStepik
from stepik_api.data_loader import load_quizes

class AnkiStepAPI:

    anki_connect_sender = AnkiConnectorSender()
    stepic_oauth = OAuthStepik()
    stepik_quizes = []
    anki_notes = None

    def __init__(self):
        self.anki_connect_sender.get_profile_of_user()

    def authorize(self, client_id: str, client_secret: str, username: str = None, password: str = None):
        self.stepic_oauth.set_credentials(client_id, client_secret, username)
        self.stepic_oauth.auth_user_password(password)

    def load_stepik_course(self, quiz_id):
        self.stepik_quizes = load_quizes(self.stepic_oauth.get_headers(), quiz_id)

    def save_quizes_anki(self):
        self.anki_connect_sender.add_notes([convert(q) for q in self.stepik_quizes])

