import requests
import datetime
import os
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

# возвращяет текст из тестового файла
def open_txt(txt_name):  
    script_directory = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_directory, 'txt', txt_name)
    with open(data_file, 'r', encoding='utf-8') as file:
        output = file.read()
    return output

# читает и возращает определнную строку из файла
def open_txt_line(number, txt_name):
    script_directory = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_directory, 'txt', txt_name)
    with open(data_file, 'r', encoding='utf-8') as file:
        if number == 1:
            output = file.readline()
            print(output)
            return output
        lines = file.readlines()
        output = lines[number]
        return output

# возращает сколько в файле строк
def count_lines(txt_name):
    script_directory = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_directory, 'txt', txt_name)
    with open(data_file, 'r', encoding='utf-8') as file:
        line_count = 0
        for line in file:
            line_count += 1
        return line_count


# token = open_txt('access_token.txt')
token = os.environ["TOKEN"]
vk_session = VkApi(token=token)
vk = vk_session.get_api()

slovar = {'привет': 'Привет!',
          'как дела': 'Хорошо, а у тебя?',
          'как дела?': 'иди нахуй(без обид)',
          'воткинск': 'Столица мира'}

# отправляет сообщениие
def send_message(id, message):  
    vk.messages.send(
        peer_id=id,
        message=message,
        random_id=get_random_id(),
    )


# история сообщений от пользователей
def history_message(event, message):
    script_directory = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_directory, 'txt/history_message.txt')
    file = open(data_file, 'a', encoding='utf-8')
    file.write(
        f"{event.datetime}\tпользователь {event.user_id} написал: {message}\n")
    file.close()
    return

# проверка слов в словаре
def first(id, message):
    if slovar.get(message) != None:
        send_message(id, slovar.get(message))


# функции для отметок
def mark1():  # +1 день (запускается каждый раз при перезагрузке программы)
    script_directory = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_directory, 'txt/marks.txt')
    file = open(data_file, 'r+', encoding='utf-8')
    n = int(file.read())
    file.seek(0, 0)
    file.truncate(0)
    file.write(str(n + 1))
    file.close()


def check_in(id):  # обнуляет дни
    script_directory = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_directory, 'txt/marks.txt')
    file = open(data_file, 'r+', encoding='utf-8')
    file.seek(0, 0)
    file.truncate(0)
    file.write('0')
    file.close()
    print('дни сброшены')
    send_message(id, 'дни успешно сброшены')


def passed():  # возращает сколько дней осталось
    script_directory = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_directory, 'txt/marks.txt')
    file = open(data_file, 'r', encoding='utf-8')
    n = file.read()
    file.close()
    return n


# переделать прослушку
# погода
def water(id, longpoll):
    api_key = open_txt('water_token.txt')
    base_url = "http://api.openweathermap.org/data/2.5/forecast?"

    send_message(id, 'Введите название города: ')

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.user_id == id:
            city_name = event.text
            break

    send_message(id, 'Выберите прогноз погоды: 1 - сейчас, 2 - на сегодня, 3 - на 3 дня вперед: ')

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.user_id == id:
            forecast_choice = event.text
            break
 

    complete_url = base_url + "appid=" + api_key + "&q=" + city_name + "&units=metric"

    response = requests.get(complete_url)
    data = response.json()

    if data["cod"] != "404":
        if forecast_choice == '1':
            current_temp = data['list'][0]['main']['temp']
            send_message(id, (f"Текущая температура в городе {city_name} : {current_temp}°C"))
            return
        elif forecast_choice == '2':
            today_temp = data['list'][0]['main']['temp']
            send_message(id, (f"Температура на сегодня в городе {city_name} : {today_temp}°C"))
            return
        elif forecast_choice == '3':
            day1_temp = data['list'][0]['main']['temp']
            day2_temp = data['list'][1]['main']['temp']
            day3_temp = data['list'][2]['main']['temp']
            send_message(id, (f"Температура на 3 дня вперед в городе {city_name} : {day1_temp}°C, {day2_temp}°C, {day3_temp}°C"))
            return
        else:
            send_message(id, "Неверный выбор прогноза погоды")
            return
    else:
        send_message(id, "Город не найден")
        return




def chatGPT():
    url = 'https://chat.openai.com/'
    session = requests.Session()
    response = session.get(url)
    print(response.text)