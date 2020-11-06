import telebot
import json
import requests
import os
import time
from telebot.types import (InlineKeyboardMarkup, ReplyKeyboardMarkup,
            KeyboardButton, InlineKeyboardButton)

bot_token = os.environ.get('BOT_TOKEN')
gis_token = os.environ.get('GIS_TOKEN')

bot = telebot.TeleBot(bot_token)

# расшифровка осадков и облачности
cloudiness = {
    0: 'ясно',
    1: 'малооблачно',
    2: 'облачно',
    3: 'пасмурно',
    101: 'переменная облачность',
}

p_type = {
    0: 'без осадков',
    1: 'дождь',
    2: 'снег',
    3: 'снег с дождём',
}

p_int = {
    0: '',
    1: 'небольшой',
    2: '',
    3: 'сильный',
}

head = {
    'X-Gismeteo-Token': gis_token,
    'Accept-Encoding': 'gzip',
}


# приветственное сообщение
@bot.message_handler(commands=['start', 'help'])
def start_message(message):
    start_text = (f'Отправьте название населённого пункта или'
                f' своё местоположение для получения погоды.')
    keyboard = ReplyKeyboardMarkup(True, True)
    txt_btn = f'Отправить моё местоположение'
    button_loc = KeyboardButton(txt_btn, request_location=True)
    keyboard.add(button_loc)
    
    bot.send_message(message.chat.id, start_text, reply_markup=keyboard)

# погода по местоположению
@bot.message_handler(content_types=['location'])
def weather_by_location(message):
    url = 'https://api.gismeteo.net/v2/weather/current/'

    param_loc = {
        'lang': 'ru',
        'latitude': message.location.latitude, 
        'longitude': message.location.longitude,
        }

    key_h = InlineKeyboardMarkup()
    btn_today = InlineKeyboardButton(text='Прогноз на сегодня',
                                        callback_data='today')
    btn_td_m = InlineKeyboardButton(text='Утро',
    callback_data=f'0 {message.location.latitude} {message.location.longitude}')
    btn_td_a = InlineKeyboardButton(text='День',
    callback_data=f'6 {message.location.latitude} {message.location.longitude}')
    btn_td_e = InlineKeyboardButton(text='Вечер',
    callback_data=f'12 {message.location.latitude} {message.location.longitude}')
    btn_td_n = InlineKeyboardButton(text='Ночь',
    callback_data=f'18 {message.location.latitude} {message.location.longitude}')
    btn_tmrrw = InlineKeyboardButton(text='Прогноз на завтра',
                                    callback_data='tomorrow')
    btn_tm_m = InlineKeyboardButton(text='Утро',
    callback_data=f'24 {message.location.latitude} {message.location.longitude}')
    btn_tm_a = InlineKeyboardButton(text='День',
    callback_data=f'30 {message.location.latitude} {message.location.longitude}')
    btn_tm_e = InlineKeyboardButton(text='Вечер',
    callback_data=f'36 {message.location.latitude} {message.location.longitude}')
    btn_tm_n = InlineKeyboardButton(text='Ночь',
    callback_data=f'42 {message.location.latitude} {message.location.longitude}')

    key_h.row(btn_today)
    key_h.row(btn_td_m, btn_td_a, btn_td_e, btn_td_n)
    key_h.row(btn_tmrrw)
    key_h.row(btn_tm_m, btn_tm_a, btn_tm_e, btn_tm_n)

    full_name = 'этом месте'

    text = weather_answer_current(url, param_loc, full_name)
    
    bot.send_message(message.chat.id, text, reply_markup=key_h,
            parse_mode='Markdown', disable_web_page_preview=True)
  
# погода по названию
@bot.message_handler(content_types=['text'])
def weather_by_id(message):

    url_search = 'https://api.gismeteo.net/v2/search/cities/'
    
    param_search = {
        'lang': 'ru',
        'query': message.text, 
        }

    cities_id = 0

    response = requests.get(url_search, params=param_search, headers=head)
        
    if response.status_code != 200:
        text = f'Нет связи с сервером погоды'
    else:
        r = json.loads(response.text)
    
        if r['response']['total'] == 0:
            text = f'Населённый пункт не найдет.'
    
        else:
            cities_id = r['response']['items'][0]['id']
            city = r['response']['items'][0]['name']
            district = r['response']['items'][0]['district']['name']
            full_name = f'{city}, {district}'

            url = f'https://api.gismeteo.net/v2/weather/current/{cities_id}/'

            param_id = {
                'lang': 'ru',
                }

            text = weather_answer_current(url, param_id, full_name)
    
    key_h = InlineKeyboardMarkup()
    btn_today = InlineKeyboardButton(text='Прогноз на сегодня',
                                        callback_data='today')
    btn_td_m = InlineKeyboardButton(text='Утро',
    callback_data=f'0 {cities_id}')
    btn_td_a = InlineKeyboardButton(text='День',
    callback_data=f'6 {cities_id}')
    btn_td_e = InlineKeyboardButton(text='Вечер',
    callback_data=f'12 {cities_id}')
    btn_td_n = InlineKeyboardButton(text='Ночь',
    callback_data=f'18 {cities_id}')
    btn_tmrrw = InlineKeyboardButton(text='Прогноз на завтра',
                                    callback_data='tomorrow')
    btn_tm_m = InlineKeyboardButton(text='Утро',
    callback_data=f'24 {cities_id}')
    btn_tm_a = InlineKeyboardButton(text='День',
    callback_data=f'30 {cities_id}')
    btn_tm_e = InlineKeyboardButton(text='Вечер',
    callback_data=f'36 {cities_id}')
    btn_tm_n = InlineKeyboardButton(text='Ночь',
    callback_data=f'42 {cities_id}')

    key_h.row(btn_today)
    key_h.row(btn_td_m, btn_td_a, btn_td_e, btn_td_n)
    key_h.row(btn_tmrrw)
    key_h.row(btn_tm_m, btn_tm_a, btn_tm_e, btn_tm_n)

    bot.send_message(message.chat.id, text, reply_markup=key_h,
            parse_mode='Markdown', disable_web_page_preview=True)

# прогноз погоды
@bot.callback_query_handler(func=lambda call: True)
def weather_forecast(call):

    data = call.data.split()

    if data[0].isdigit():
        
        hours = int(data[0])

        if len(data) == 2:# прогноз по ID населенного пункта
            cities_id = data[1]

            param_for = {
                'lang': 'ru',
                'days': 3,
            }

            url = f'https://api.gismeteo.net/v2/weather/forecast/{cities_id}/'

            answer = weather_answer_forecast(url, param_for, hours)
        
        elif len(data) == 3:# прогноз по координатам
            latitude = data[1]
            longitude = data[2]
            
            param_for = {
                'lang': 'ru',
                'latitude': latitude, 
                'longitude': longitude,
                'days': 3,
            }

            url = 'https://api.gismeteo.net/v2/weather/forecast/'

            answer = weather_answer_forecast(url, param_for, hours)

        else:
            answer = f'Упс.. неизвестный запрос.'
        
        bot.send_message(call.message.chat.id, answer)
    
    elif data[0] == 'today':
        bot.answer_callback_query(callback_query_id=call.id, text='Выберите время суток')
    elif data[0] == 'tomorrow':
        bot.answer_callback_query(callback_query_id=call.id, text='Выберите время суток')
    else: # на случай неправильного call.data
        answer = f'Похоже мой создатель ещё не научил меня обрабатывать такие запросы.'
       
        bot.send_message(call.message.chat.id, answer)


# запрос текущей погоды
def weather_answer_current(url, param, full_name):
    
    response = requests.get(url, params=param, headers=head)

    if response.status_code != 200: # проверка доступности сервера
        answer = f'Нет связи с сервером погоды'
    else:
        weather = json.loads(response.text)

        temp = weather['response']['temperature']['air']['C']
        wind = weather['response']['wind']['speed']['m_s']
        cloud_type = weather['response']['cloudiness']['type']
        cloud = cloudiness[cloud_type]
        precip_type = weather['response']['precipitation']['type']
        precip_int = weather['response']['precipitation']['intensity']
        precip_amount = weather['response']['precipitation']['amount']
        

        sn='+'
        if temp <= 0:# знак перед значением температуры
            sn = ''
        
        if precip_amount is None or precip_amount == 0:# ответ если нет осадков
            answer = (f'[Сейчас](https://www.gismeteo.ru/) в {full_name}: {sn}{temp} \xb0С, {cloud},'
                    f' ветер {wind} м/с, {p_int[precip_int]} {p_type[precip_type]}.')
        else:
            answer = (f'[Сейчас](https://www.gismeteo.ru/) в {full_name}: {sn}{temp} \xb0С, {cloud}, ветер {wind} м/с,'
                    f' {p_int[precip_int]} {p_type[precip_type]} {precip_amount} мм.')
        
    return answer

# запрос прогноза погоды
def weather_answer_forecast(url, param, hours):
    
    response = requests.get(url, params=param, headers=head)

    if response.status_code != 200: # проверка доступности сервера
        answer = f'Нет связи с сервером погоды'
    else:
        weather = json.loads(response.text)
        # расчет смещения времени до 6:00 утра
        local_date = weather['response'][0]['date']['local']
        local_time = local_date.split()[1]
        h = int(local_time.split(':')[0])
        m = int(local_time.split(':')[1])
        offset = (360 - (h*60 + m))/60
        # расчет порядка прогноза в словаре
        count = round((offset + hours)/3)

        temp = weather['response'][count]['temperature']['air']['C']
        wind = weather['response'][count]['wind']['speed']['m_s']
        cloud_type = weather['response'][count]['cloudiness']['type']
        cloud = cloudiness[cloud_type]
        precip_type = weather['response'][count]['precipitation']['type']
        precip_int = weather['response'][count]['precipitation']['intensity']
        precip_amount = weather['response'][count]['precipitation']['amount']
        time_forecast = weather['response'][count]['date']['unix']

        p_f = 'будет'
        if time_forecast < time.time():
            p_f = 'было'

        sn = '+'
        if temp <= 0:# знак перед значением температуры
            sn = ''

        time_of_day = {
            0: 'Сегодня утром',
            6: 'Сегодня днём',
            12: 'Сегодня вечером',
            18: 'Сегодня ночью',
            24: 'Завтра утром',
            30: 'Завтра днём',
            36: 'Завтра вечером',
            42: 'Завтра ночью',
        }
        
        if precip_amount is None or precip_amount == 0:# ответ если нет осадков
            answer = (f'{time_of_day[hours]} {p_f}: {sn}{temp} \xb0С, {cloud},'
                    f' ветер {wind} м/с, {p_int[precip_int]} {p_type[precip_type]}.')
        else:
            answer = (f'{time_of_day[hours]} {p_f}: {sn}{temp} \xb0С, {cloud}, ветер {wind} м/с,'
                    f' {p_int[precip_int]} {p_type[precip_type]} {precip_amount} мм.')
        
    return answer

bot.polling()