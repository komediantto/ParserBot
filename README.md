# ParserBot

## Описание

Telegram-бот парсер для актуальной ленты новостей города Брянск.

## Технологии

Aiogram, redis, docker, BeatifulSoup

## Как запустить

Создать .env файл в корне проекта вида:

```env
TOKEN = <токен вашего бота>
CHANNEL_ID = <id вашего канала>
ANOTHER_CHANNEL_ID = <id второго канала>
WEATHER_API_KEY = <api ключ openweather>
MCHS = 'https://32.mchs.gov.ru/deyatelnost/press-centr/vse-novosti?news_type=Штормовые+и+экстренные+предупреждения&news_date_from=&news_date_to='

WEATHER = 'https://api.openweathermap.org/data/2.5/forecast'

HOLY = 'https://my-calend.ru/holidays'

NEWBR = 'https://newsbryansk.ru/cat_economy.html,https://newsbryansk.ru/cat_jkh.html,https://newsbryansk.ru/cat_investigation.html'

RIA = 'https://ria.ru/incidents/'
BGA = 'https://bga32.ru/category/news/'
BO = 'http://www.bryanskobl.ru/news'
GUB_ACS = 'https://guberniya.tv/category/proisshestviya/,https://guberniya.tv/category/kriminal/'

GUB_CRMNL = 'https://guberniya.tv/category/kriminal/'

BRGAZ = 'https://www.bragazeta.ru/news/category/news/society/'

BN = 'https://bryansknovosti.ru/'

COMMENT_GROUP_ID = <id группы с комментариями>

TELEGRAPH_TOKEN = <ваш telegraph токен>

URL = 'https://telegra.ph/'

PROJECT_SLUG = 'ParserBot'
```

Из корневой директории запустить docker-compose

```bash
docker-compose up -d
```

Бот запускается по команде /start и делает следующее:

1. Каждое утро отправляет:
 a. Сводку МЧС
 б. Прогноз погоды на сегодня
 в. Гороскоп на сегодня
 г. Сегодняшние праздники
2. Проверяет ряд новостных сайтов города Брянск и по мере их появления постит их в ваш канал
