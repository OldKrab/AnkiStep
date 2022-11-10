# AnkiStep

Приложение для быстрого экспорта решенных задач из курса на [Stepik](https://stepik.org) 
в колоду [Anki](https://apps.ankiweb.net/) карт.

## Prereferences

Для использования необходимо, чтобы на устройсве был установлен Anki с расширением AnkiConnect:

1. Открыть: tools -> Add-ons -> Get Add-ons...  
2. Ввести [код Anki-connect](https://ankiweb.net/shared/info/2055492159)
3. Перезапустить приложение

## Авторизация 

Для авторизации создайте данные для oauth2 авторизации на [Stepik](https://stepik.org/oauth2/applications/):

Client type: confidential, Authorization Grant Type: client-credentials. 

Сохраните данные. Используйте client id и client secret для авторизации в приложении.

## Сборка 
Для сборки под vscode ввести в консоли (в папке проекта)

export PYTHONPATH=.
