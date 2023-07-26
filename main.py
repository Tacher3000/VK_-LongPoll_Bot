import requests
import yadisk
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
                    f.send_message(240453492, 'в маркс больше 7 дней')


def main():
    print('запустилось')
    # token = f.open_txt('access_token.txt')
    token = os.environ['TOKEN']
    vk_session = VkApi(token=token)
    vk = vk_session.get_api()
    longpoll = MyVkLongPoll(vk_session)

    # +1 день но временно отключен
    # f.mark1()

    # оповещает о перезапуске в будущем убрать(тест)
    # f.send_message(240453492, 'произошел перезапуск')

    # проверка на колличество дней
    if int(f.passed()) >= 7:
        f.send_message(240453492, 'в маркс больше 7 дней')

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

            # если слово подходит к списку сообщение - ответ (временно отключен)
            # f.first(id, message)

            # проверяет есть ли человек который пишет в списке администрации
            for i in range(f.count_lines('administrators.txt')):
                if id == int(f.open_txt_line(i, 'administrators.txt')):
                    if (message == '!отметиться' or message == '!очисть' or message == '!очистить'):
                        f.check_in(id)
                    elif (message == '!сколько осталось?' or message == '!остаток' or message == '!сколько'):
                        f.send_message(id, f.passed())
                    elif message == '!проверка':
                        f.send_message(id, 'проверки пока что нет')
                    elif message == '!команды':
                        f.send_message(id, f.open_txt('administrators_comands.txt'))
                    elif message == '!погода':
                        f.water(id, longpoll)
                    elif message == '!отправь':
                        f.send_message(
                            id, 'Ты точно хочешь это сделать? [Y - да, N - нет]')
                        # немного переделать!!!!!!
                        for e in longpoll.listen():
                            if e.type == VkEventType.MESSAGE_NEW and e.to_me:
                                if e.text == 'Y':
                                    # удаляем старый файл если он есть
                                    try:
                                        os.remove('txt/diary.txt')
                                        print('Файл успешно удален.')
                                    except FileNotFoundError:
                                        print('Файл для удаления не найден.')

                                    # скачиваем новый с яндекс диска
                                    yadisk_token = os.environ['YADISK_TOKEN']
                                    y = yadisk.YaDisk(
                                        token=yadisk_token)
                                    y.download('/diary.txt', 'txt/diary.txt')

                                    # отправляем файл каждому человеку из списка
                                    for j in range(f.count_lines('trusted_people.txt')):
                                        f.send_txt_file(
                                            int(f.open_txt_line(j, 'trusted_people.txt')), 'мой дневник, сообщение оптравлено автоматически', 'diary.txt')
                                    break
                                else:
                                    f.send_message(id, 'Отправка отменена')
                                    break


            # проверка на людей из списка проверенных людей
            for i in range(f.count_lines('trusted_people.txt')):
                if id == int(f.open_txt_line(i, 'trusted_people.txt')):
                    if (message == '!отправь'):
                        # удаляем старый файл если он есть
                        try:
                            os.remove('txt/diary.txt')
                            print('Файл успешно удален.')
                        except FileNotFoundError:
                            print('Файл для удаления не найден.')
                        
                        # скачиваем новый с яндекс диска
                        yadisk_token = os.environ['YADISK_TOKEN']
                        y = yadisk.YaDisk(
                            token=yadisk_token)
                        y.download('/diary.txt', 'txt/diary.txt')

                        # отправляем файл
                        f.send_txt_file(
                            id, 'мой дневник, сообщение оптравлено автоматически', 'diary.txt')
                    elif message == '!команды':
                        f.send_message(id, f.open_txt('trusted_people_comands.txt'))
                    elif message == '!погода':
                        f.water(id, longpoll)
                    else:
                        f.send_message(
                            id, 'Ларочка, к сожалению, я всего лишь бот')
            
            if message == '!команды':
                f.send_message(id, f.open_txt('comands.txt'))
            elif message == '!погода':
                f.water(id, longpoll)


if __name__ == '__main__':
    main()
