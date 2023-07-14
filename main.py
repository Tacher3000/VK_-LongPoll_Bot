import requests
import time
import os
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType
import function as f

# чтобы не выключался каждую ночь + когда срабатывает исключение добавляется +1 
class MyVkLongPoll(VkLongPoll):
    def listen(self):
        while True:
            try:
                for event in self.check():
                    yield event
            except Exception as e:
                print('error', e)
                time.sleep(10)
                
                 # +1 день
                f.mark1()

                # проверка на колличество дней
                if int(f.passed()) >= 7:
                    f.send_message(240453492, "в маркс больше 7 дней")


def main():
    print("запустилось")
    # token = f.open_txt('access_token.txt')
    vk_session = VkApi(token=TOKEN)
    longpoll = MyVkLongPoll(vk_session)
    
    # +1 день но временно отключен
    # f.mark1()

    # оповещает о перезапуске в будущем убрать(тест)
    f.send_message(240453492, "произошел перезапуск")

    # проверка на колличество дней
    if int(f.passed()) >= 7:
        f.send_message(240453492, "в маркс больше 7 дней")
    
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:

            # message
            message = event.text

            # добавление в историю
            f.history_message(event, message)

            # преобразование слова в нижний регистр
            message = message.lower()

            # id
            id = event.user_id

            # если слово подходит к списку сообщение - ответ
            f.first(id, message)

            # проверяет есть ли человек который пишет в списке администрации
            for i in range(f.count_lines('administrators.txt')):
                if id == int(f.open_txt_line(i, 'administrators.txt')):
                    if message == 'отметиться' or message == 'очисть' or message == 'очистить':
                        f.check_in(id)
                    elif message == 'сколько осталось?' or message == 'остаток' or message == 'сколько':
                        f.send_message(id, f.passed())

            if message == '!команды':
                f.send_message(id, f.open_txt('comands.txt'))
            elif message == '!погода':
                f.water(id, longpoll)
            elif message == '!перевод':
                f.send_message(id, 'временно не работает')


if __name__ == '__main__':
    main()
