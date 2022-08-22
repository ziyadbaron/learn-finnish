import telebot
from telebot import types
from Constants import API_KEY
import finnish_language_database
import random


bot = telebot.TeleBot(API_KEY)


def processing_steps_message(num):
    if num == 0:
        return ' 1  __ __ __ __ __ __ __ __ __ '
    elif num == 1:
        return '__  2  __ __ __ __ __ __ __ __ '
    elif num == 2:
        return '__ __  3  __ __ __ __ __ __ __ '
    elif num == 3:
        return '__ __ __  4  __ __ __ __ __ __ '
    elif num == 4:
        return '__ __ __ __  5  __ __ __ __ __ '
    elif num == 5:
        return '__ __ __ __ __  6  __ __ __ __ '
    elif num == 6:
        return '__ __ __ __ __ __  7  __ __ __ '
    elif num == 7:
        return '__ __ __ __ __ __ __  8  __ __ '
    elif num == 8:
        return '__ __ __ __ __ __ __ __  9  __ '
    elif num == 9:
        return ' __ __ __ __ __ __ __ __ __ 10 '


def show_keyboard_choices(msg, btn1, btn2, btn3, btn4, the_message):

    markup = types.ReplyKeyboardMarkup(row_width=2)
    button1 = types.KeyboardButton(btn1)
    button2 = types.KeyboardButton(btn2)
    button3 = types.KeyboardButton(btn3)
    button4 = types.KeyboardButton(btn4)
    if btn3 == "":
        markup.add(button1, button2)
    elif btn4 == "":
        markup.add(button1, button2, button3)
    else:
        markup.add(button1, button2, button3, button4)
    bot.send_message(chat_id=msg.chat.id, text=the_message,
                     parse_mode="html", reply_markup=markup)


def show_home_menu(msg, user, previous_learning=1):

    if previous_learning:
        if msg.text == 'finish the test' or msg.text == 'End learning' or msg.text == 'Home 🏠':
            user.testing_tag = 0
            user.learning_tag = 0

        beginning_message = "<b>Hi!</b> I'm Ziyad's bot for teaching language \n\n\
                            \nPlease choose one of the <b>choices</b> "
    else:
        beginning_message = "<b>Sorry!</b>\n\n You have to learn some word before making a test"

    show_keyboard_choices(msg, "Learn new words", "Make test", "",
                          "", beginning_message)

# —————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————


def have_user_learned_words(user):
    connection = finnish_language_database.connect()
    user_id = user.user_id
    finnish_language_database.create_customer_table(connection, user_id)
    table_content = finnish_language_database.check_if_table_is_empty(
        connection, user_id)

    if table_content[0][0] == 0:
        return False
    else:
        return True


def create_learning_word_list(user):
    Words_list = []
    connection = finnish_language_database.connect()

    # create user table if not exist
    user_id = user.user_id
    finnish_language_database.create_customer_table(connection, user_id)

    # add 10 words for user table
    Words_list = finnish_language_database.choose_new_words(
        connection, 10, 0)
    for i in Words_list:
        word_id, _, _ = i
        finnish_language_database.insert_word_to_user(
            connection, user_id, word_id)

    # shuffle the learning word list
    user.learn_words_list = random.sample(Words_list, len(Words_list))

    # we just begin the learning so we set the counter to 0 and activate learning tag
    user.learn_words_counter = 0
    user.learning_tag = 1
    user.testing_tag = 0


def process_learning(msg, user):
    _, fin, eng = user.learn_words_list[user.learn_words_counter]
    processing_steps = processing_steps_message(user.learn_words_counter)

    # if it is the first learning word (we just begin or we pressing previous)
    if user.learn_words_counter == 0:
        the_message = f'  🇫🇮      <b> = </b>      🇬🇧 \n  \n \n<b>〈  {fin} = {eng}  〉</b>\n   \n\n' + processing_steps
        # show keyboard choices without the previous button and with a message to show finnish and English words
        show_keyboard_choices(msg, "Home 🏠", "next word", "", "", the_message)

    # if it is not the first or last learning word
    elif 0 < user.learn_words_counter and user.learn_words_counter < 9:
        the_message = f'  🇫🇮      <b> = </b>      🇬🇧\n  \n \n<b>〈  {fin} = {eng}  〉</b>\n   \n\n' + processing_steps
        show_keyboard_choices(msg, "previous word",
                              "next word", "Home 🏠", "", the_message)

        # if it is the last learning word
    elif user.learn_words_counter == 9:
        the_message = f'  🇫🇮     <b>  =  </b>      🇬🇧 \n  \n<b>〈  {fin} = {eng}  〉</b>n   \n' + processing_steps
        # show keyboard choices with end learning and a message to show finnish and English words
        show_keyboard_choices(msg, "previous word",
                              "End learning", "Home 🏠", "", the_message)

    else:
        print('something is wrong (out of if else) ')

# —————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————


def create_test_answer_list(connection, user_id, user):
    # empty the answer list
    user.test_answer_list.clear()

    # create list for wrong answers for the test
    wrong_answer_list = finnish_language_database.choose_random_user_words(
        connection, user_id, 3)

    # create test answer list for multiple choice and shuffle it randomly
    _, _, eng = user.test_word_list[user.test_counter]
    user.test_answer_list.append(eng)
    for i in wrong_answer_list:
        _, _, eng = i
        user.test_answer_list.append(eng)
    random.shuffle(user.test_answer_list)


def process_first_question(msg, user):
    # make testing tag on
    user.testing_tag = 1
    user.learning_tag = 0

    user_id = msg.from_user.id
    connection = finnish_language_database.connect()

    # create word lists from user list and set the counter to 0 and clear the wrong answers list
    user.test_word_list = finnish_language_database.choose_random_user_words(
        connection, user_id, 10)
    user.test_counter = 0
    user.test_wrong_answers.clear()

    create_test_answer_list(connection, user_id, user)

    _, fin, _ = user.test_word_list[user.test_counter]
    processing_steps = processing_steps_message(user.test_counter)
    the_message = f' What this <b>Finnish</b> 🇫🇮 word mean ? \n \n <b>〈  {fin}  〉</b> \n\n' + processing_steps
    show_keyboard_choices(msg, user.test_answer_list[0], user.test_answer_list[1],
                          user.test_answer_list[2], user.test_answer_list[3], the_message)


def process_right_answer(msg, user):
    user_id = msg.from_user.id
    _, previous_word_fin, _ = user.test_word_list[user.test_counter]

    user.test_counter += 1
    connection = finnish_language_database.connect()

    # if there's more questions go to the next world
    if user.test_counter < len(user.test_word_list):
        create_test_answer_list(connection, user_id, user)

        _, new_word_fin, _ = user.test_word_list[user.test_counter]
        processing_steps = processing_steps_message(user.test_counter)
        right_answer_message = f'Right answer ✅✅✅ \n\n <b>〈  {previous_word_fin} = {msg.text}  〉</b> \n\n\
                                \n<b>Now,</b> what does this <b>Finnish</b> 🇫🇮 word mean ? \n\
                                \n<b>〈  {new_word_fin}  〉</b> \n\n' + processing_steps
        show_keyboard_choices(msg, user.test_answer_list[0], user.test_answer_list[1],
                              user.test_answer_list[2], user.test_answer_list[3], right_answer_message)

    # when the test is finished show the result of the test
    else:
        user.testing_tag = 0
        right_answers = len(user.test_word_list) - \
            len(user.test_wrong_answers)

        congratulation_message = f'Right answer ✅✅✅ \n\n <b>〈  {previous_word_fin} = {msg.text}  〉</b> \n\n\
            \n<b>Congratulation 🥳🚬</b>you finished the test 📝 😍\n\nYou got  <b>{right_answers}  right answers ✅✅ </b>\n\
            \nand  <b>{len(user.test_wrong_answers)}  wrong answers❌❌ </b>'
        show_keyboard_choices(
            msg, "finish the test", "Make new test", "Home 🏠", "", congratulation_message)


def process_wrong_answer(msg, user):
    _, previous_word_fin, _ = user.test_word_list[user.test_counter]

    # if answer is wrong add it to the wrong answers list and repeat the question
    if len(user.test_wrong_answers) == 0:
        user.test_wrong_answers.append(user.test_counter)
    elif user.test_wrong_answers[-1] != user.test_counter:
        user.test_wrong_answers.append(user.test_counter)

    processing_steps = processing_steps_message(user.test_counter)
    Wrong_answer_message = f' Wrong answer ❌❌❌ \n \n  <b>〈  {previous_word_fin}  ❌  {msg.text}  〉</b> \n\
        \n<b>Again!</b> What does this <b>Finnish</b> 🇫🇮 word mean ? \n\n <b>〈  {previous_word_fin}  〉</b> \n\n' + processing_steps
    show_keyboard_choices(msg, user.test_answer_list[0], user.test_answer_list[1],
                          user.test_answer_list[2], user.test_answer_list[3], Wrong_answer_message)
