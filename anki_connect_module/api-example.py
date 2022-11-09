from anki_connect_sender import AnkiConnectorSender

def test():
    ankiConnector = AnkiConnectorSender()

    conf = ankiConnector.get_deck_config("Default")
    ankiConnector.save_deck_config(conf)

    ankiConnector.create_deck("new deck")
    deck_names = ankiConnector.get_deck_names()

    res = ankiConnector.add_card_gui({
        "deckName": "Default",
        "modelName": "Cloze",
        "fields": {
            "Text": "The capital of Romania is {{c1::Bucharest}} 3",
            "Extra": "Romania is a country in Europe 3"
        },
        "tags": [
            "countries"
        ],
        "picture": [{
            "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/EU-Romania.svg/285px-EU-Romania.svg.png",
            "filename": "romania.png",
            "fields": [
                "Extra"
            ]
        }]
    })

    note = ankiConnector.add_note({
        "deckName": "Default",
        "modelName": "Basic",
        "fields": {
            "Front": "front content",
            "Back": "back content"
        },
        "tags": [
            "yomichan111"
        ],
        "audio": [{
            "url": "https://assets.languagepod101.com/dictionary/japanese/audiomp3.php?kanji=猫&kana=ねこ",
            "filename": "yomichan_ねこ_猫.mp3",
            "skipHash": "7e2c2f954ef6051373ba916f000168dc",
            "fields": [
                "Front"
            ]
        }],
        "video": [{
            "url": "https://cdn.videvo.net/videvo_files/video/free/2015-06/small_watermarked/Contador_Glam_preview.mp4",
            "filename": "countdown.mp4",
            "skipHash": "4117e8aab0d37534d9c8eac362388bbe",
            "fields": [
                "Back"
            ]
        }],
        "picture": [{
            "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/A_black_cat_named_Tilly.jpg/220px-A_black_cat_named_Tilly.jpg",
            "filename": "black_cat.jpg",
            "skipHash": "8d6e4646dfae812bf39651b59d7429ce",
            "fields": [
                "Back"
            ]
        }]
    })

    ankiConnector.delete_notes([note])


test()