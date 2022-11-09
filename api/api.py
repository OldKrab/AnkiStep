
from anki_connect_module.anki_connect_sender import AnkiConnectorSender
from quiz_converter.converter import convert
from stepik_api.authorisation import OAuthStepik
from stepik_api.data_loader import DataLoader

class AnkiStepAPI:

    anki_connect_sender = AnkiConnectorSender()
    stepic_oauth = OAuthStepik()
    loader = DataLoader()
    stepik_quizes = None
    anki_notes = None

    def __init__(self):
        self.anki_connect_sender.get_profile_of_user()

    def authorize(self, client_id: str, client_secret: str, username: str = None, password: str = None):
        self.stepic_oauth.set_credentials(client_id, client_secret, username)
        self.stepic_oauth.auth_user_password(password)
        self.loader.set_loader(self.stepic_oauth)

    def load_stepik_course(self, quiz_id):
        self.stepik_quizes = self.loader.load_quizes(quiz_id)

    def save_quizes_anki(self):
        self.anki_connect_sender.add_notes([convert(q) for q in self.stepik_quizes])

