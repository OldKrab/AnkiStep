# AnkiStep

Приложение для быстрого экспорта решенных задач из курса на [Stepik](https://stepik.org) 
в колоду [Anki](https://apps.ankiweb.net/) карт.

## Prereferences

Для использования необходимо, чтобы на устройсве был установлен Anki с расширением AnkiConnect:

1. Открыть: tools -> Add-ons -> Get Add-ons...  
2. Ввести [код Anki-connect](https://ankiweb.net/shared/info/2055492159)
3. Перезапустить приложение

Для корректного отображения формул на устройстве должен быть установлен latex.

## Установка 

Склонировать репозиторий, вызвать <code> pip install . </code> в корневой папке.

## Команды

### Авторизация 

Для авторизации создайте данные для OAuth2 авторизации на [Stepik](https://stepik.org/oauth2/applications/):

<code>Client type: confidential </code>,

 <code>Authorization Grant Type: client-credentials</code>.

Сохраните данные. Используйте client id и client secret для авторизации в приложении.

### Загрузка недавних курсов пользователя  

<code>ankistep last-courses <count=5> </code>

### Экспорт заданий из курса 

<code>ankistep convert <course_id> </code>


## Недоработки 

При повторном экспорте курса информация о прогрессе в Anki пропадает 

[Демо](https://youtu.be/kwSNqm8XckQ)