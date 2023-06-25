import os
import httpx
import redis
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import datetime
from dotenv import load_dotenv
import logging


logging.basicConfig(filename=f'{__name__}.log',
                    level=logging.INFO,
                    filemode='w',
                    encoding='UTF-8')


load_dotenv()

ua = UserAgent()

headers = {
    'user-agent': str(ua.chrome)
}

redis = redis.Redis('redis_server', 6379, 0)


def get_urgent_information():
    """
    It gets the latest news from the website of the Ministry of Emergency
    Situations of Russia
    :return: A dictionary with the title of the news
    as the key and the link to the
    news as the value.
    """
    url = os.getenv('MCHS')
    urgent_news = {}
    try:
        response = httpx.get(url, headers=headers)
        result = response.text
        soup = BeautifulSoup(result, 'lxml')
        today = int(datetime.datetime.now().strftime('%d'))
        things_list = soup.find_all('div', class_='articles-item')
        for thing in things_list:
            thing_date = thing.find('span', class_='articles-item__date').text
            if today - int(thing_date[:2]) <= 1:
                thing_title = thing.find('a',
                                         class_='articles-item__title').text
                thing_href = 'https://32.mchs.gov.ru' + thing.find(
                    'a', class_='articles-item__title').get('href')
                urgent_news[thing_title] = thing_href
        return urgent_news
    except Exception as e:
        logging.error('Нет ответа от сервера')
        logging.error(e)


def get_weather():
    """
    It gets the weather forecast for today and tomorrow from an API and
    returns it in a dictionary.
    :return: A dictionary with two keys: today and tomorrow.
    """
    url = os.getenv('WEATHER')
    forecast_dict = {'today': {},
                     'tomorrow': {}}
    try:
        response = httpx.get(
            url,
            params={
                'id': 571476,
                'lang': 'ru',
                'units': 'metric',
                'APPID': os.getenv('WEATHER_API_KEY')
                }, headers=headers)
        result = response.json()
        today = int(datetime.datetime.now().strftime('%d'))
        for i in result['list']:
            if int(i['dt_txt'][8:10]) - today == 1:
                forecast = (
                    i['dt_txt'][11:] + '{0:+3.0f} '.format(i['main']['temp'])
                    + i['weather'][0]['description']
                    )
                if i['weather'][0]['id'] == 803:
                    forecast_dict['tomorrow'][forecast] = (
                                            'images/облачно с прояснением.png')
                elif i['weather'][0]['main'] == 'Snow':
                    forecast_dict['tomorrow'][forecast] = 'images/снег.png'
                elif i['weather'][0]['main'] == 'Rain':
                    forecast_dict['tomorrow'][forecast] = 'images/дождь.png'
                elif i['weather'][0]['main'] == 'Clear':
                    forecast_dict['tomorrow'][forecast] = 'images/ясно.png'
                elif i['weather'][0]['main'] == 'Thunderstorm':
                    forecast_dict['tomorrow'][forecast] = (
                        'images/дождь с гроза.png')
                elif i['weather'][0]['main'] == 'Clouds':
                    forecast_dict['tomorrow'][forecast] = 'images/облачно.png'
            elif int(i['dt_txt'][8:10]) == today:
                forecast = (
                    i['dt_txt'][11:] + '{0:+3.0f} '.format(i['main']['temp'])
                    + i['weather'][0]['description']
                    )
                if i['weather'][0]['id'] == 803:
                    forecast_dict['today'][forecast] = (
                                            'images/облачно с прояснением.png')
                elif i['weather'][0]['main'] == 'Snow':
                    forecast_dict['today'][forecast] = 'images/снег.png'
                elif i['weather'][0]['main'] == 'Rain':
                    forecast_dict['today'][forecast] = 'images/дождь.png'
                elif i['weather'][0]['main'] == 'Clear':
                    forecast_dict['today'][forecast] = 'images/ясно.png'
                elif i['weather'][0]['main'] == 'Thunderstorm':
                    forecast_dict['today'][forecast] = (
                        'images/дождь с гроза.png')
                elif i['weather'][0]['main'] == 'Clouds':
                    forecast_dict['today'][forecast] = 'images/облачно.png'
        return forecast_dict
    except Exception as e:
        logging.error("Сайт недоступен")
        logging.error(e)


def get_horoscope():
    """
    It gets the horoscope for each sign from the website and returns a
    dictionary with the sign name as the key and the horoscope text and
    image path as the value.
    :return: A dictionary with the name of the sign as the key and a tuple as
    the value. The tuple contains the horoscope text and the image path.
    """
    horoscope = {}
    signs = {
        'aries': ['Овен', 'images/овен.png'],
        'taurus': ['Телец', 'images/Телец.png'],
        'gemini': ['Близнецы', 'images/блезнецы.png'],
        'cancer': ['Рак', 'images/рак.png'],
        'leo': ['Лев', 'images/лев.png'],
        'virgo': ['Дева', 'images/дева.png'],
        'libra': ['Весы', 'images/весы.png'],
        'scorpio': ['Скорпион', 'images/скорпион.png'],
        'sagittarius': ['Стрелец', 'images/стрелец.png'],
        'capricorn': ['Козерог', 'images/козерог.png'],
        'aquarius': ['Водолей', 'images/водолей.png'],
        'pisces': ['Рыбы', 'images/рыбы.png'],
    }
    for sign in signs.items():
        try:
            response = httpx.get(
                f'https://horo.mail.ru/prediction/{sign[0]}/today/',
                headers=headers)
            result = response.text
            soup = BeautifulSoup(result, 'lxml')
            horoscope_text = soup.find(
                'div', class_=('article__item article__item_alignment_left '
                               'article__item_html')).text
            horoscope[sign[1][0]] = horoscope_text, sign[1][1]
        except Exception as e:
            horoscope['Exception horoscope'] = e
    return horoscope


def get_holidays():
    """
    It takes a url, makes a request to that url, parses the response, and
    returns a list of holidays
    :return: A list of holidays
    """
    url = os.getenv('HOLY')
    holidays = []
    try:
        response = httpx.get(url, headers=headers)
        result = response.text
        soup = BeautifulSoup(result, 'lxml')
        holidays_list = soup.find('ul', class_='holidays-items').find_all('li')
        for holiday in holidays_list:
            holiday = holiday.text[:-5]
            holidays.append(holiday)
        return holidays
    except Exception as e:
        logging.error(f"Сайт {url} недоступен")
        logging.error(e)


def get_urgent_information_polling():
    """
    It gets the latest news from the site, checks if it's already in the
    database, if not, it adds it to the database and returns the message.
    :return: a message.
    """
    url = os.getenv('MCHS')
    try:
        response = httpx.get(url, headers=headers)
        result = response.text
        soup = BeautifulSoup(result, 'lxml')
        title = soup.find('a', class_='articles-item__title').text
        thing_href = soup.find(
            'div', class_='articles-item').find(
                'a', class_='articles-item__title').get('href')
        response = httpx.get(f'https://32.mchs.gov.ru{thing_href}',
                             headers=headers)
        result = response.text
        soup = BeautifulSoup(result, 'lxml')
        text = soup.find('div', itemprop='articleBody').find_all('p', limit=15)
        message = f'{title}\n\n'
        for p in text:
            message += p.text
        image = soup.find('div', class_='public').find('img').get('src')
        image_url = 'https://32.mchs.gov.ru' + image
        if redis.get(message) is not None:
            if redis.get(message) != image_url.encode():
                redis.set(message, image_url)
                return message
            else:
                return None
        else:
            logging.info(f'Ключа {message[:10]} не существует.')
            redis.set(message, image_url)
            return message
    except Exception as e:
        logging.error(f"Сайт {url} недоступен")
        logging.error(e)


def get_info_from_newbryansk():
    """
    It gets the latest news from the site, checks if the image is in the redis
    database, if not, it adds it to the database and returns the image and the
    text of the news.
    :return: a tuple of two elements.
    """
    urls = os.getenv('NEWBR').split(',')
    for url in urls:
        try:
            response = httpx.get(url, headers=headers, timeout=15.0)
            result = response.text
            soup = BeautifulSoup(result, 'lxml')
            new_href = soup.find('div',
                                 class_='col-xs-12 page-container'
                                 ).find('div').find(
                                    'a', class_='post-title').get('href')
            new_href_url = 'https://newsbryansk.ru/' + new_href
            response = httpx.get(new_href_url, headers=headers)
            result = response.text
            soup = BeautifulSoup(result, 'lxml')
            title = soup.find('div',
                              class_='col-xs-12 page-container'
                              ).find('article').find('h1').text
            text = soup.find('div',
                             class_='col-xs-12 page-container'
                             ).find('article').find_all('p', limit=6)
            image = soup.find('div',
                              class_='col-xs-12 page-container'
                              ).find('img').get('src')
            message = f'{title}\n\n'
            for p in text:
                message += p.text
            message += f'\n\nИсточник: {url}'
            if redis.get(image) is not None:
                if image.encode() not in redis.keys():
                    redis.set(image, message, datetime.timedelta(days=2))
                    yield image, message
                else:
                    yield None
            else:
                logging.info(f'Ключа {image} не существует.')
                redis.set(image, message, datetime.timedelta(days=2))
                yield image, message
        except Exception as e:
            logging.error(f"Сайт {url} недоступен")
            logging.error(e)


def get_info_from_ria():
    """
    It gets the latest news from the site, parses it, and returns the image and
    text of the news
    :return: a tuple of two elements: image and message.
    """
    url = os.getenv('RIA')
    try:
        response = httpx.get(url, headers=headers)
        result = response.text
        soup = BeautifulSoup(result, 'lxml')
        new_href = soup.find(
            'div', class_='list list-tags'
            ).find('div', class_='list-item'
                   ).find('div', class_='list-item__content'
                          ).find('a',
                                 class_=('list-item__title '
                                         'color-font-hover-only')
                                 ).get('href')
        response = httpx.get(new_href, headers=headers)
        result = response.text
        soup = BeautifulSoup(result, 'lxml')
        title = soup.find('div', class_='article__title').text
        text = soup.find_all('div', class_='article__block', limit=2)
        message = f'{title}\n\n'
        for p in text:
            try:
                abzac = p.find('div', class_='article__text').text
                message += abzac + '\n\n'
            except Exception:
                abzac = p.find('div',
                               class_='article__quote-text m-small').text
                message += abzac
        message += f'\nИсточник: {url}'
        image = soup.find('div', class_='media').find('img').get('src')
        if redis.get(image) is not None:
            if image.encode() not in redis.keys():
                redis.set(image, message, datetime.timedelta(days=2))
                return image, message
            else:
                return None
        else:
            logging.info(f'Ключа {image} не существует.')
            redis.set(image, message, datetime.timedelta(days=2))
            return image, message
    except Exception as e:
        logging.error(f"Сайт {url} недоступен")
        logging.error(e)


def get_info_from_bga():
    """
    It gets the latest news from the site, parses it, and returns the image and
    text of the news
    :return: a tuple of two elements: image and message.
    """
    url = os.getenv('BGA')
    try:
        response = httpx.get(url, headers=headers)
        result = response.text
        soup = BeautifulSoup(result, 'lxml')
        new_title = soup.find(
            'div', class_='c9'
            ).find('div', class_='oneNewsBlock'
                   ).find('a').get('title')
        new_href = soup.find(
            'div', class_='c9'
            ).find('div', class_='oneNewsBlock'
                   ).find('a').get('href')
        image = soup.find(
            'div', class_='c9'
            ).find('div', class_='oneNewsBlock'
                   ).find('img').get('src')
        response = httpx.get(new_href, headers=headers)
        result = response.text
        soup = BeautifulSoup(result, 'lxml')
        message = f'{new_title}\n\n'
        text = soup.find('div', class_='c9').find_all(['h2', 'p'], limit=5)
        for p in text:
            message += p.text
        message += f'\n\nИсточник: {url}'
        if redis.get(image) is not None:
            if image.encode() not in redis.keys():
                redis.set(image, message, datetime.timedelta(days=2))
                return image, message
            else:
                return None
        else:
            logging.info(f'Ключа {image} не существует.')
            redis.set(image, message, datetime.timedelta(days=2))
            return image, message
    except Exception as e:
        logging.error(f"Сайт {url} недоступен")
        logging.error(e)


def get_info_from_bryanskobl():
    """
    It gets the latest news from the site, parses it, and returns the image and
    text of the news
    :return: a tuple of two values.
    """
    url = os.getenv('BO')
    try:
        response = httpx.get(url, headers=headers)

        result = response.text

        soup = BeautifulSoup(result, 'lxml')
        new_title = soup.find(
            'div', class_='grid_12'
            ).find('div', class_='grid_10 omega'
                   ).find('div', class_='news-header-item'
                          ).find('a').text
        new_href = soup.find(
            'div', class_='grid_12'
            ).find('div', class_='grid_10 omega'
                   ).find('div', class_='news-header-item'
                          ).find('a').get('href')
        new_href_url = 'http://www.bryanskobl.ru' + new_href
        response = httpx.get(new_href_url, headers=headers)
        result = response.text
        soup = BeautifulSoup(result, 'lxml')
        text = soup.find('div', class_='grid_12'
                         ).find('div',
                                class_='news-content').find_all('p', limit=3)
        try:
            image = 'http://www.bryanskobl.ru' + soup.find(
                    'div', class_='grid_12'
                    ).find('div', class_='grid_8 alpha photo-container'
                           ).find('img', class_='image-border').get('src')
        except Exception:
            image = None
        message = f'{new_title}\n\n'
        for p in text:
            message += p.text + '\n'
        message += f'\nИсточник: {url}'
        if redis.get(new_href_url) is not None:
            if new_href_url.encode() not in redis.keys():
                redis.set(new_href_url, message, datetime.timedelta(days=2))
                return image, message
            else:
                return None
        else:
            logging.info(f'Ключа {image} не существует.')
            redis.set(new_href_url, message, datetime.timedelta(days=2))
            return image, message
    except Exception as e:
        logging.error(f"Сайт {url} недоступен")
        logging.error(e)


def get_info_from_gub():
    urls = os.getenv('GUB_ACS').split(',')
    for url in urls:
        try:
            response = httpx.get(url, headers=headers)
        except Exception as e:
            logging.error(f"Сайт {url} недоступен")
            logging.error(e)
        result = response.text
        soup = BeautifulSoup(result, 'lxml')
        article = soup.find('div', class_='article'
                            ).find('a').get('href')
        response = httpx.get(article, headers=headers)
        result = response.text
        soup = BeautifulSoup(result, 'lxml')
        title = soup.find('div', class_='single_post').find('h1').text
        try:
            image = soup.find(
                'div', class_='thecontent').find('img').get('src')
        except Exception:
            image = None
        text = soup.find('div', class_='thecontent').find_all('p', limit=2)
        message = f'{title}\n\n'
        for p in text:
            message += p.text + '\n\n'
        message += f'\nИсточник: {url}'
        if redis.get(article) is not None:
            if article.encode() not in redis.keys():
                redis.set(article, message, datetime.timedelta(days=2))
                yield image, message
            else:
                return None
        else:
            logging.info(f'Ключа {image} не существует.')
            redis.set(article, message, datetime.timedelta(days=2))
            yield image, message


def get_info_from_brgaz():
    url = os.getenv('BRGAZ')
    try:
        response = httpx.get(url, headers=headers)
    except Exception:
        logging.error(f'Сайт {url} недоступен')
    result = response.text
    soup = BeautifulSoup(result, 'lxml')
    article = soup.find('div',
                        class_='col-lg-12 top-cat-news').find('a').get('href')
    response = httpx.get(article, headers=headers)
    result = response.text
    soup = BeautifulSoup(result, 'lxml')
    title = soup.find('h1').text
    image = soup.find('article').find('img',
                                      class_='single-top-img').get('src')
    text = soup.find('div', class_='video-show').find_all('p', limit=2)
    message = f'{title}\n\n'
    for p in text:
        message += p.text + '\n\n'
    message += f'\nИсточник: {url}'
    if redis.get(image) is not None:
        if image.encode() not in redis.keys():
            redis.set(image, message, datetime.timedelta(days=2))
            return image, message
        else:
            return None
    else:
        logging.info(f'Ключа {image} не существует.')
        redis.set(image, message, datetime.timedelta(days=2))
        return image, message


def get_info_from_bn():
    url = os.getenv('BN')
    response = httpx.get(url, headers=headers)
    result = response.text
    soup = BeautifulSoup(result, 'lxml')
    article = soup.find('div', class_='loop'
                        ).find('article').find('a').get('href')
    response = httpx.get(article, headers=headers)
    result = response.text
    soup = BeautifulSoup(result, 'lxml')
    title = soup.find('h1').text
    image = soup.find('div', class_='loop').find('img').get('src')
    text = soup.find('div', class_='entry-content').find_all('p', limit=2)
    message = f'{title}\n\n'
    for p in text:
        message += p.text + '\n\n'
    if redis.get(image) is not None:
        if image.encode() not in redis.keys():
            redis.set(image, message, datetime.timedelta(days=2))
            return image, message
        else:
            return None
    else:
        logging.info(f'Ключа {image} не существует.')
        redis.set(image, message, datetime.timedelta(days=2))
        return image, message
