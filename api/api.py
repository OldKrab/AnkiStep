from anki_connect_module.anki_connect_sender import AnkiConnectorSender
from quiz_converter.converter import convert
from stepik_api.authorisation import OAuthStepik
from stepik_api.data_loader import load_quizes


class AnkiStepAPI:
    anki_connect_sender = AnkiConnectorSender()
    stepic_oauth = OAuthStepik()
    stepik_quizes = []
    anki_notes = None

    def __init__(self) -> None:
        self.check_anki_connect()

    def check_anki_connect(self):
        self.anki_connect_sender.get_profile_of_user()

    def authorize(self, client_id: str, client_secret: str):
        self.stepic_oauth.set_credentials(client_id, client_secret)
        self.stepic_oauth.auth_user_password()

    def load_stepik_course(self, course_id):
        self.stepik_quizes = load_quizes(self.stepic_oauth.get_headers(), course_id)

    def save_quizes_anki(self):
        cards = [convert(q) for q in self.stepik_quizes]

        deck_names_to_add = set()
        for c in cards:
            deck_names_to_add.add(c['deckName'])

        self.anki_connect_sender.delete_decks(list(deck_names_to_add), True)
        for d in deck_names_to_add:
            self.anki_connect_sender.create_deck(d)

        self.anki_connect_sender.add_notes(cards)
