import requests
import time
import os
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType
import function as f


import os
from dotenv import load_dotenv
load_dotenv()


# через сколько дней попросят отметиться
warning = 2

# через сколько дней без отметок отправится дневник
deadline = 3


slovar = {'привет': 'Привет!',
          'как дела': 'Хорошо, а у тебя?',
          'как дела?': 'иди нахуй(без обид)',
          'воткинск': 'Столица мира'}

# чтобы не выключался каждую ночь + когда срабатывает исключение добавляется +1 и происходит проверка на колличество дней


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
                if int(f.passed()) >= warning and int(f.passed()) < deadline:
                    f.send_message(
                        240453492, f'с последней отметки прошло {warning} или больше дней. Пожалуйста отметься')
                    f.send_message(
                        240453492, f'через столько дней:{deadline - warning} дневник будет отправлен')

                if int(f.passed()) >= deadline:
                    f.send_message(
                        240453492, f'в маркс больше {deadline} дней')
                    f.diary()


def main():
    print('запустилось')
    # token = f.open_txt('access_token.txt')
    token = os.environ['TOKEN']
    vk_session = VkApi(token=token)
    vk = vk_session.get_api()
    longpoll = MyVkLongPoll(vk_session)

    # оповещает о перезапуске в будущем убрать(тест)
    # f.send_message(240453492, 'произошел перезапуск')

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            k = 0
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
                        k += 1
                    elif (message == '!сколько осталось?' or message == '!остаток' or message == '!сколько'):
                        f.send_message(id, f.passed())
                        k += 1
                    elif message == '!проверка':
                        f.send_message(id, 'проверки пока что нет')
                        k += 1
                    elif message == '!команды':
                        f.send_message(id, f.open_txt(
                            'administrators_comands.txt'))
                        k += 1
                    elif message == '!погода':
                        f.water(id, longpoll)
                        k += 1
                    elif slovar.get(message) != None:
                        f.send_message(id, slovar.get(message))
                        k += 1
                    elif message == '!отправь':
                        f.send_message(
                            id, 'Ты точно хочешь это сделать? [Y - да, N - нет]')
                        # немного переделать!!!!!!
                        for e in longpoll.listen():
                            if e.type == VkEventType.MESSAGE_NEW and e.to_me:
                                if e.text == 'Y':
                                    f.diary()
                                    break
                                else:
                                    f.send_message(id, 'Отправка отменена')
                                    break
                        k += 1
                    elif message == '!рандом':
                        random_image = f.download_images_yadisk()
                        f.send_images(id, '', random_image)
                        try:
                            os.remove('data/images/' + random_image)
                        except FileNotFoundError:
                            print(
                                'изображение для удаления не найдено(что странно).')
                        k += 1
                    elif message == '!прибавить':
                        f.mark1()
                        f.send_message(id, 'добавлен 1 день')
                        k += 1
                    elif message == '!посмотреть':
                        f.me_diary(id, '')
                        k += 1
                    elif message == '!дополнить' or message == '!добавить':
                        f.send_message(id, 'введите что хотите добавить')
                        for e in longpoll.listen():
                            if e.type == VkEventType.MESSAGE_NEW and e.to_me:
                                f.add_diary(e.text)
                                break
                        f.send_message(id, 'сообщение добавлено')
                        k += 1

            if k == 1:
                continue

            # проверка на людей из списка проверенных людей
            for i in range(f.count_lines('trusted_people.txt')):
                if id == int(f.open_txt_line(i, 'trusted_people.txt')):
                    if (message == '!отправь'):
                        f.diary()
                        k += 1
                    elif slovar.get(message) != None:
                        f.send_message(id, slovar.get(message))
                        k += 1
                    elif message == '!команды':
                        f.send_message(id, f.open_txt(
                            'trusted_people_comands.txt'))
                        k += 1
                    elif message == '!погода':
                        f.water(id, longpoll)
                        k += 1
                    elif message == '!рандом':
                        random_image = f.download_images_yadisk()
                        f.send_images(id, '', random_image)
                        try:
                            os.remove('data/images/' + random_image)
                        except FileNotFoundError:
                            print(
                                'изображение для удаления не найдено(что странно).')
                        k += 1
                    else:
                        f.send_message(
                            id, 'Ларочка, к сожалению, я всего лишь бот')
                        k += 1

            if k == 1:
                continue

            if message == '!команды':
                f.send_message(id, f.open_txt('comands.txt'))
            elif message == '!погода':
                f.water(id, longpoll)
            elif message == '!рандом':
                        random_image = f.download_images_yadisk()
                        f.send_images(id, '', random_image)
                        try:
                            os.remove('data/images/' + random_image)
                        except FileNotFoundError:
                            print(
                                'изображение для удаления не найдено(что странно).')
                        k += 1


if __name__ == '__main__':
    main()
