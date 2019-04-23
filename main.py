import logging
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler
from telegram import InlineQueryResultArticle, InputTextMessageContent


def read_file(filename: str) -> str:
    try:
        file_handle = open(filename)
        file_text = file_handle.read()
        file_handle.close()
        return file_text
    except FileNotFoundError:
        print('file %s not found', filename)
        return False

#этот метод требуется телеграмом.
def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")


def fuck(bot, update, args):
    for name in args:
        bot.send_message(chat_id=update.message.chat_id, text='Эй ' + name + ' ' + 'Да ты, мудило... Ты че моих друзей обижаешь?')


#этот метод ищет вхождение слова в рецепт среди спика рецептов
def search(bot, update, args):
    bzu = read_file('bzu.txt')
    solutions = bzu.split('\n\n')
    result = set(solutions)
    #  проверяем список запрошеный пользователем
    for user_arg in args:
        temp_set = set()
        # с каждой итерацией отсеивает лишние рецепты
        for solution in solutions:
            if solution.lower().find(user_arg.lower()) != -1:
                temp_set.add(solution)
        result = result.intersection(temp_set)
    if len(result) == 0:
        result.add('no solutions found...')
    result_for_sending = '\n========================================\n'.join(result)
    with open('solution.txt', 'w') as file:
        file.write(result_for_sending)
    # bot.send_message(chat_id=update.message.chat_id, text=result_for_sending)
    bot.send_document(chat_id=update.message.chat_id, document=open('solution.txt', 'rb'))
    return result_for_sending


#преобразует в верхний регистр
def caps(bot, update, args):
    text_caps = ' '.join(args).upper()
    bot.send_message(chat_id=update.message.chat_id, text=text_caps)

#преобразует в верхний регистр
def inline_caps(bot, update):
    query = update.inline_query.query
    if not query:
        return
    results = list()
    results.append(
        InlineQueryResultArticle(
            id=query.upper(),
            title='search',
            input_message_content=InputTextMessageContent(search(bot, update, query))
        )#,
        # InlineQueryResultArticle(
        #     id=query.upper(),
        #     title='help',
        #     input_message_content=InputTextMessageContent(query.upper())
        # )
    )
    update.inline_query.answer(results)
    # bot.answer_inline_query(update.inline_query.id, results)

#выдать сообщение, если команда не была распознана
def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")

#повторяет за пользователем
def echo(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=str('echo: ' + update.message.text))


def help(bot, update, args):
    help_text = read_file('help.txt')
    bot.send_message(chat_id=update.message.chat_id, text=help_text)


def run():

    #читаем токен из файла
    token = read_file('token.txt')
    
    #читаем БЗУ из файла
    bzu = read_file('bzu.txt')
    
    #зарбивка БЗУ на отдельные рецепты
    solutions = bzu.split('\n\n')

    #передаем боту токен подключения
    bot = telegram.Bot(token = token)

    #инициализируем объект-обновлятор
    updater = Updater(token = token)

    #инициализируем систему диспетчиризации
    dispatcher = updater.dispatcher


    #далее определяются "рычаги управления" ботом и что они смогут делать
    
    #передаем название фун-ции котрая выполнится при команде /start
    start_handler = CommandHandler('start', start)
    #регистрируем в диспетчере новый функционал ("рычажок")
    dispatcher.add_handler(start_handler)

    fuck_handler = CommandHandler('fuck', fuck, pass_args=True)
    dispatcher.add_handler(fuck_handler)

    search_handler = CommandHandler('search', search, pass_args=True)
    dispatcher.add_handler(search_handler)

    caps_handler = CommandHandler('caps', caps, pass_args=True)
    dispatcher.add_handler(caps_handler)

    inline_caps_handler = InlineQueryHandler(inline_caps)
    dispatcher.add_handler(inline_caps_handler)

    help_handler = CommandHandler('help', help, pass_args=True)
    dispatcher.add_handler(help_handler)

    echo_handler = MessageHandler(Filters.text, echo)
    dispatcher.add_handler(echo_handler)

    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)


    #вызываем метод получеия обнов с сервака
    updater.start_polling()
	#при таком методе, наша прога просто исполняет бесконечный цикл
	#и на каждой итерации она спрашивает у сервера, не появилось ли сообщений для нашего бота
	#Такой подход плох тем что создает излишнюю нагрузку на наше железо(или арендуемое) и сервера телеграма
	#Необходимо указать другой метод обновления. И настроить его работу если нужно.

    updater.idle()
