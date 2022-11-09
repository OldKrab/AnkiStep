import json
import urllib.request


class AnkiConnectorSender:
    localhost_address = 'http://localhost:8765'

    @staticmethod
    def _request(action, **params):
        return {'action': action, 'params': params, 'version': 6}

    @classmethod
    def invoke(cls, action, **params):
        requestJson = json.dumps(cls._request(action, **params)).encode('utf-8')
        response = json.load(urllib.request.urlopen(urllib.request.Request(cls.localhost_address, requestJson)))
        if len(response) != 2:
            raise Exception('response has an unexpected number of fields')
        if 'error' not in response:
            raise Exception('response is missing required error field')
        if 'result' not in response:
            raise Exception('response is missing required result field')
        if response['error'] is not None:
            raise Exception(response['error'])
        return response['result']

    # actions with cards and notes
    # https://foosoft.net/projects/anki-connect/index.html#note-actions
    @classmethod
    def add_card_gui(cls, GUI_card: dict):
        return cls.invoke("guiAddCards", note=GUI_card)

    @classmethod
    def get_cards_info(cls, cards: list):
        return cls.invoke('cardsInfo', cards=cards)

    @classmethod
    def add_notes(cls, notes: list):
        return cls.invoke("addNotes", notes=[note for note in notes])

    @classmethod
    def add_note(cls, note: dict):
        return cls.invoke("addNote", note=note)

    @classmethod
    def update_note_fields(cls, note_id: int, note_fields: map):
        note_fields["id"] = note_id
        return cls.invoke("updateNoteFields", note=note_fields)

    @classmethod
    def delete_notes(cls, notes_id: list):
        return cls.invoke("deleteNotes", notes=notes_id)

    # tags
    @classmethod
    def add_tags(cls, notes_ids: list, tags: str):
        return cls.invoke("addTags", notes=notes_ids, tags=tags)

    @classmethod
    def remove_tags(cls, notes_ids: list, tags: str):
        return cls.invoke("removeTags", notes=notes_ids, tags=tags)

    @classmethod
    def get_tags(cls):
        return cls.invoke("getTags")

    @classmethod
    def clear_unused_tags(cls):
        return cls.invoke("clearUnusedTags")

    """ https://docs.ankiweb.net/searching.html """

    @classmethod
    def find_notes(cls, query: str):
        return cls.invoke("findNotes", query=query)

    # actions with deck
    # https://foosoft.net/projects/anki-connect/index.html#deck-actions
    @classmethod
    def get_deck_names(cls):
        return cls.invoke('deckNames')

    @classmethod
    def get_deck_names_of_cards_ids(cls, cards_ids: list):
        return cls.invoke('getDecks', cards=cards_ids)

    @classmethod
    def get_deck_names_and_ids(cls):
        return cls.invoke('deckNamesAndIds')

    @classmethod
    def create_deck(cls, deck_name):
        return cls.invoke('createDeck', deck=deck_name)

    # configure actions
    @classmethod
    def get_deck_config(cls, deck_name: str):
        return cls.invoke("getDeckConfig", deck=deck_name)

    @classmethod
    def save_deck_config(cls, deck_config: dict):
        return cls.invoke("saveDeckConfig", config=deck_config)

    @classmethod
    def delete_decks(cls, decks: list, delete_cards_too=False):
        return cls.invoke("deleteDecks", decks=decks, cardsToo=delete_cards_too)

    # actions with models
    # https://foosoft.net/projects/anki-connect/index.html#model-actions
    # TODO
    #

    # global configuration actions/settings
    # https://foosoft.net/projects/anki-connect/index.html#miscellaneous-actions
    @classmethod
    def sync_local_store_with_ankiweb(cls):
        return cls.invoke("sync")

    @classmethod
    def get_profile_of_user(cls):
        return cls.invoke("getProfiles")

    @classmethod
    def export_package(cls, deck_name: str, path: str, include_schedule=False):
        return cls.invoke("exportPackage", deck=deck_name, path=path, includeSched=include_schedule)

