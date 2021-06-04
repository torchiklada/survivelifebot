from telebot import TeleBot, types
import random
import time

TOKEN = "1702202626:AAE4EKgbS557Ykfk99DKG0U5nnAd76ZGJ5c"

# states =
# 0 - старт
# 1 - выбор работы
# 2 - выбор жилья
# 3 - процесс игры
# 4 - попросить помощь
# 5 - конец игры

pictures = {
    0: "https://media1.giphy.com/media/eJ4j2VnYOZU8qJU3Py/giphy.gif",
    1: "https://soho-catering.ru/images/shop/products/original/1478513700.6651.jpg",
    2: "https://www.metaltg.ru/upload/iblock/b57/b57339a9b7a8daadad1d325f1350af20.jpg",
    3: "https://image.freepik.com/free-photo/happy-telephone-operators-customer-service-representative-man-in-call-center_100800-751.jpg",
    4: "https://media1.tenor.com/images/d187f6cc75de75a9a2dd611a43e1391e/tenor.gif?itemid=15523929"
}

vacancy = {
    1: "🔹Официант🔹 (оформление по ТК, 13% налоги)\nПолный день, 4 рабочих / 3 выходных в неделю, 7:30-20:45 / 8:30-21:30 с гибкими выходными, 60.000-80.000₽ в месяц.\nСтавка: 300р/час + чаевые\nТребования: Иметь отлично развитые коммуникативные навыки, быть позитивным, энергичным, стрессоустойчивым и пунктуальным.",
    2: "🔹Курьер🔹 (оформление в качестве самозанятого, налог 6%)\nЗаработная плата до 3400р в день, выплаты ежедневные.\nКурьерские поручения можно выполнять любым способом передвижения.\nТребования: Целеустремленность, ответственность, готовность к работе по городу.",
    3: "🔹Оператор call-центра🔹 (оформление по ТК, налог 13%)\nРабота из дома, график работы 2/2 с 9:00 до 21:00, зарплата 30-40.000 в месяц.\nТребования: наличие ПК и стабильного интернета, хорошая дикция, грамотная речь и высокая клиентоориентированность."
}

def health_bar(hearts):
    health_bar = ""
    for _ in range(hearts):
        health_bar += "💚"
    return health_bar


state = {}
health = {}
money = {}
job = {}
salary = {}
rent = {}
days = {}  # количество дней, прошедших с начала игры
relations = {}  # отношения с родственниками
can_ask_help = {}  # просил ли уже помощи с деньгами у родственников
events = [i for i in range(1, 11)]  # номера событий
current_event = {}  # событие текущего дня
took_vacation = {}  # сколько дней в текущей неделе не работал -> вычитается из зарплаты
work_out = {}  # есть ли абонемент в спорт зал -> повышает здоровье на +1 в неделю

bot = TeleBot(TOKEN)


@bot.message_handler(commands=["start"])
def start_game(message):
    user = message.chat.id
    state[user] = 0
    process_state(user)


@bot.callback_query_handler(func=lambda call: True)
def user_answer(call):
    user = call.message.chat.id
    process_answer(user, call.data)


def process_state(user):
    kb = types.InlineKeyboardMarkup()

    if state[user] == 0:
        health[user] = 5
        money[user] = 80000
        days[user] = 1
        relations[user] = 1
        can_ask_help[user] = 1
        took_vacation[user] = 0
        work_out[user] = 0

        bot.send_video(user, pictures[4])
        time.sleep(1)
        bot.send_message(user, "По данным на февраль 2021 года, в России около 4 миллионов безработных.")
        time.sleep(3)
        bot.send_message(user, "По сравнению с февралем 2020 года безработица в РФ выросла на 24%.")
        time.sleep(3)
        bot.send_message(user, "Многие из них потеряли работу из-за пандемии.")
        time.sleep(3)
        bot.send_message(user, "Теперь представьте, что вы один из них.")
        time.sleep(3)
        bot.send_message(user, "Вы потеряли вашу квартиру и из ваших сбережений у вас осталось 80.000₽")
        time.sleep(3)

        state[user] = 1
        process_state(user)

    elif state[user] == 1:
        kb.add(types.InlineKeyboardButton(text="Официант", callback_data="Официант"))
        kb.add(types.InlineKeyboardButton(text="Курьер", callback_data="Курьер"))
        kb.add(types.InlineKeyboardButton(text="Оператор call-центра", callback_data="Оператор call-центра"))
        bot.send_message(user, "Найти работу: ", reply_markup=kb)

    elif state[user] == 2:
        # time.sleep(1)
        kb.add(types.InlineKeyboardButton(text="Подмосковье", callback_data="Подмосковье"))
        kb.add(types.InlineKeyboardButton(text="Москва", callback_data="Москва"))
        bot.send_message(user, "Найти съёмную квартиру: ", reply_markup=kb)
        # time.sleep(1)
        bot.send_message(user,
                         "Вы можете снимать квартиру в пригороде, тогда жильё обойдётся дешевле, но придётся тратить больше денег и времени на проезд до работы.")

    elif state[user] == 3:
        if money[user] <= 0 or health[user] <= 0:
            state[user] = 4
            process_state(user)

        else:
            if job[user] == 'Курьер':
                if took_vacation[user] == 0:
                    money[user] += 3000
                bot.send_message(user, "Вам выплатили зарплату за день!")
                took_vacation[user] = 0

            if days[user] % 10 == 0:
                if job[user] == 'Курьер':
                    health[user] -= 1
                elif job[user] == 'Официант':
                    health[user] -= 0.5
                    bot.send_message(user, "Вам выплатили зарплату за 10 дней!")
                    # time.sleep(1)
                    money[user] += salary[user] - salary[user] / 5 * took_vacation[user]
                else:
                    bot.send_message(user, "Вам выплатили зарплату за 10 дней!")
                    # time.sleep(1)
                    money[user] += salary[user] - salary[user] / 5 * took_vacation[user]

                took_vacation[user] = 0

            if days[user] % 7 == 0 and work_out[user]:
                health[user] += 1
                health[user] = min(10, health[user])

            if money[user] >= 0 and health[user] >= 0:
                bot.send_message(user, 'День ' + str(days[user]) + '\nЗдоровье: ' + health_bar(
                    health[user]) + '\nДеньги: ' + str(int(money[user])) + '₽')
                time.sleep(2)

            random_event = random.choice(events)

            if days[user] % 7 == 0:
                random_event = 0
                current_event[user] = 0
                kb.add(types.InlineKeyboardButton(text="🍜 Лапша быстрого приготовления и полуфабрикаты (1000₽)",
                                                  callback_data="1"))
                kb.add(types.InlineKeyboardButton(text="🥫 Замороженные овощи, крупы и консервы (2000₽)",
                                                  callback_data="2"))
                kb.add(
                    types.InlineKeyboardButton(text="🥗 Свежие овощи и фрукты, мясо и рыба (4000₽)", callback_data="3"))
                bot.send_message(user, '❓Вам нужно купить продукты на неделю:', reply_markup=kb)

            if random_event == 1:
                events.remove(1)
                current_event[user] = 1
                kb.add(types.InlineKeyboardButton(text="Полететь на самолёте на похороны (билеты -10.000₽)",
                                                  callback_data="Полететь"))
                kb.add(types.InlineKeyboardButton(text="Не поехать на похороны.", callback_data="Остаться"))
                bot.send_message(user,
                                 '❗️У вас умер дедушка, который жил в другом городе. Похороны проходят через три дня.',
                                 reply_markup=kb)

            if random_event == 2:
                current_event[user] = 2
                kb.add(types.InlineKeyboardButton(text="Продолжить работать несмотря на боль.",
                                                  callback_data="Продолжить"))
                kb.add(types.InlineKeyboardButton(text="Взять выходной за свой счёт.", callback_data="Выходной"))
                bot.send_message(user,
                                 '❗️Вы только начали свою смену, но вдруг заметили, что из-за постоянных нагрузок на работе у вас появилась боль в спине.',
                                 reply_markup=kb)

            if random_event == 3:
                current_event[user] = 3
                kb.add(types.InlineKeyboardButton(text="Сходить к психотерапевту (-5.000₽ за приём).",
                                                  callback_data="Сходить"))
                kb.add(
                    types.InlineKeyboardButton(text="Притвориться, что всё нормально.", callback_data="Рип менталочка"))
                bot.send_message(user,
                                 '❗️Постоянная неуверенность в своем будущем сказывается на вашем ментальном здоровье. Вы думаете, что возможно у вас депрессия.',
                                 reply_markup=kb)

            if random_event == 4:
                current_event[user] = 4
                kb.add(types.InlineKeyboardButton(text="Согласиться (-1000₽).", callback_data="Согласиться"))
                kb.add(
                    types.InlineKeyboardButton(text="Сказать, что забыл кошелек дома.", callback_data="Не согласиться"))
                bot.send_message(user, '❗️У вашего коллеги день рождения и вам предлагают скинуться на подарок.',
                                 reply_markup=kb)

            if random_event == 5:
                # через год добавить снова
                current_event[user] = 5
                kb.add(types.InlineKeyboardButton(text="Купить клубную карту в спортзал на год (-20.000₽).",
                                                  callback_data="Купить"))
                kb.add(
                    types.InlineKeyboardButton(text="Отложить эту затею до лучших времен.", callback_data="Отложить"))
                bot.send_message(user,
                                 '❗️Регулярные занятия спортом полезны для здоровья и снижают ваш уровень стресса.',
                                 reply_markup=kb)

            if random_event == 6:
                events.remove(6)
                current_event[user] = 6
                kb.add(types.InlineKeyboardButton(text="Сходить к врачу на обследование.", callback_data="Сходить"))
                kb.add(types.InlineKeyboardButton(text="Проигнорировать.", callback_data="Проигнорировать"))
                bot.send_message(user,
                                 '❗️Последнее время вы стали испытывать резкую боль в грудной клетке. Вы знаете, что у вас есть склонность к болезням сердца.',
                                 reply_markup=kb)

            if random_event == 7:
                current_event[user] = 7
                kb.add(types.InlineKeyboardButton(text="Оплатить (-15.000₽).", callback_data="Оплатить"))
                bot.send_message(user,
                                 '❗️Вы случайно затопили соседей снизу. Хозяин квартиры настаивает, чтобы вы сами оплатили ущерб.',
                                 reply_markup=kb)

            if random_event == 8:
                current_event[user] = 8
                kb.add(types.InlineKeyboardButton(text="Отдать деньги на лекарства (-5.000₽).", callback_data="Отдать"))
                kb.add(types.InlineKeyboardButton(text="Отказать.", callback_data="Отказать"))
                bot.send_message(user,
                                 '❗️Вашей маме срочно требуются лекарства, но у неё не хватает на них денег. Она попросила вас ей помочь.',
                                 reply_markup=kb)

            if random_event == 9:
                events.remove(9)
                current_event[user] = 9
                kb.add(types.InlineKeyboardButton(text="Пройти курс (увеличение зарплаты на 25%).",
                                                  callback_data="Пройти"))
                bot.send_message(user, '❗️Ваша компания предлагает вам пройти курс повышения квалификации.',
                                 reply_markup=kb)

            if random_event == 10:
                current_event[user] = 10
                kb.add(types.InlineKeyboardButton(text="Взять на сегодня отпуск за свой счет.",
                                                  callback_data="Взять отпуск"))
                kb.add(types.InlineKeyboardButton(text="Пойти на работу несмотря на плохое самочувствие.",
                                                  callback_data="Пойти на работу"))
                bot.send_message(user,
                                 '❗️Началась эпидемия гриппа и вы чувствуете, что у вас поднялась температура и вас знобит.',
                                 reply_markup=kb)

            days[user] += 1

    elif state[user] == 4:
        if health[user] <= 0:
            bot.send_message(user, "Вы потратили всё здоровье, удачи в другой жизни!")
            bot.send_video(user, pictures[0])
            state[user] = 5

        else:
            if money[user] <= 0:
                if relations[user] == 1:
                    if can_ask_help[user] == 1:
                        can_ask_help[user] = 0
                        kb = types.InlineKeyboardMarkup()
                        kb.add(types.InlineKeyboardButton(text="Попросить одолжить 5.000₽",
                                                          callback_data="Попросить одолжить 5.000₽"))
                        kb.add(types.InlineKeyboardButton(text="Попросить одолжить 10.000₽",
                                                          callback_data="Попросить одолжить 10.000₽"))
                        bot.send_message(user,
                                         "У вас закончились деньги, но вы можете попросить помощи у родственников.",
                                         reply_markup=kb)
                    else:
                        bot.send_message(user,
                                         "У вас снова закончились деньги? Вы уже просили помощи у родственников. Вам больше не к кому обратиться.")
                        bot.send_video(user, pictures[0])
                        state[user] = 5
                        process_state(user)
                else:
                    bot.send_message(user,
                                     "К сожалению, отношения с родственниками испорчены, и они отказываются помочь вам.")
                    bot.send_video(user, pictures[0])
                    state[user] = 5
                    process_state(user)

    elif state[user] == 5:
        time.sleep(3)
        kb.add(types.InlineKeyboardButton(text="Начать игру заново", callback_data="Начать игру заново"))
        bot.send_message(user, 'Попробуйте сыграть еще раз!', reply_markup=kb)


def process_answer(user, answer):
    if state[user] == 1:
        if answer == "Официант":
            bot.send_photo(user, pictures[1])
            bot.send_message(user, vacancy[1])
            salary[user] = 10000

        if answer == "Курьер":
            bot.send_photo(user, pictures[2])
            bot.send_message(user, vacancy[2])
            salary[user] = 15000

        if answer == "Оператор call-центра":
            bot.send_photo(user, pictures[3])
            bot.send_message(user, vacancy[3])
            salary[user] = 8000

        job[user] = answer
        state[user] = 2
        time.sleep(3)

    elif state[user] == 2:
        if answer == "Подмосковье":
            bot.send_message(user, "20 тыс/мес + залог + комиссия = 50 тыс (первый месяц).")
            time.sleep(1)
            money[user] -= 50000
            rent[user] = 20000
            bot.send_message(user, "У вас осталось " + str(money[user]) + "₽")

        elif answer == "Москва":
            bot.send_message(user, "30 тыс/мес + залог + комиссия = 75 тыс (первый месяц).")
            time.sleep(1)
            money[user] -= 75000
            rent[user] = 30000
            bot.send_message(user, "У вас осталось " + str(money[user]) + "₽")

        time.sleep(1)
        state[user] = 3

    elif state[user] == 3:

        if money[user] > 0:

            if current_event[user] == 0:
                if answer == '1':
                    money[user] -= 1000
                    health[user] -= 1
                    bot.send_message(user, 'Такая еда плохо влияет на здоровье в долгосрочной перспективе.')

                if answer == '2':
                    money[user] -= 2000

                if answer == '3':
                    money[user] -= 4000
                    health[user] += 1
                    bot.send_message(user, 'Такая еда полезна и положительно скажется на здоровье.')

            if current_event[user] == 1:
                if answer == 'Полететь':
                    money[user] -= 10000
                else:
                    bot.send_message(user,
                                     'На вас обиделись родственники, и не захотят вам помогать, когда вам понадобится помощь.')
                    relations[user] = 0

            if current_event[user] == 2:
                if answer == 'Продолжить':
                    health[user] -= 1
                else:
                    took_vacation[user] += 1

            if current_event[user] == 3:
                if answer == 'Сходить':
                    money[user] -= 5000
                else:
                    health[user] -= 1

            if current_event[user] == 4:
                if answer == 'Согласиться':
                    money[user] -= 1000
                else:
                    bot.send_message(user,
                                     'На вас обиделись коллеги, и не захотят вам помогать, когда вам понадобится помощь.')

            if current_event[user] == 5:
                if answer == 'Купить':
                    events.remove(5)
                    money[user] -= 20000
                    work_out[user] = 1

            if current_event[user] == 6:
                if answer == 'Сходить':
                    if random.randint(0, 1) == 1:
                        bot.send_message(user, 'У вас обнаружен порок сердца. Срочная операция будет стоить 40.000₽')
                        money[user] -= 40000
                    else:
                        bot.send_message(user, 'Ничего не обнаружено, врач советует вам чаще заниматься спортом.')
                else:
                    health[user] -= 1

            if current_event[user] == 7:
                money[user] -= 15000

            if current_event[user] == 8:
                if answer == 'Отдать':
                    money[user] -= 5000
                else:
                    bot.send_message(user, 'Ваша мама умерла, вы чувствуете свою вину в её смерти.')
                    health[user] -= 2

            if current_event[user] == 9:
                salary[user] += 0.25 * salary[user]

            if current_event[user] == 10:
                if answer == 'Взять отпуск':
                    took_vacation[user] += 1
                else:
                    health[user] -= 1

            time.sleep(3)

    elif state[user] == 4:
        if answer == 'Попросить одолжить 5.000₽':
            money[user] += 5000
            state[user] = 3
        elif answer == 'Попросить одолжить 10.000₽':
            money[user] += 10000
            state[user] = 3

    elif state[user] == 5:
        if answer == 'Начать игру заново':
            state[user] = 0

    process_state(user)


bot.polling(none_stop=True)
