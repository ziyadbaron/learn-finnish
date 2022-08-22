import telebot
from Constants import API_KEY
import functions

users = {}


class User:
    def __init__(self, chat_id, user_id, test_word_list, test_answer_list, test_counter,
                 test_wrong_answers, testing_tag, learn_words_list, learn_words_counter, learning_tag):
        self.chat_id = chat_id
        self.user_id = user_id

        self.test_word_list = test_word_list
        self.test_answer_list = test_answer_list
        self.test_counter = test_counter
        self.test_wrong_answers = test_wrong_answers
        self.testing_tag = testing_tag

        self.learn_words_list = learn_words_list
        self.learn_words_counter = learn_words_counter
        self.learning_tag = learning_tag


bot = telebot.TeleBot(API_KEY)


@bot.message_handler(func=lambda msg: msg.text)
def control(msg):

    user_id = str(msg.from_user.id)
    chat_id = str(msg.chat.id)

    # if it is a new user add it to the list of users
    if not user_id in users:
        test_word_list = 0
        test_answer_list = ['a', 'b', 'c', 'd']
        test_counter = 0
        test_wrong_answers = []
        testing_tag = 0

        learn_words_list = []
        learn_words_counter = 0
        learning_tag = 0

        users[user_id] = User(chat_id, user_id, test_word_list, test_answer_list,
                              test_counter, test_wrong_answers, testing_tag, learn_words_list,
                              learn_words_counter, learning_tag)
        functions.show_home_menu(msg, users[user_id])

    # if the user choose to make test but he/she haven't learned any word to make test ask him/ her to learn some words
    elif msg.text == 'Make test' and not functions.have_user_learned_words(users[user_id]):
        functions.show_home_menu(msg, users[user_id], previous_learning=0)

    # for learning
    # if the user begin learning or he/she is in the learning process and he/she didn't finish learning
    elif msg.text == 'Learn new words' or \
            (users[user_id].learning_tag == 1 and msg.text != 'End learning' and msg.text != 'Home 🏠'):
        # if the user begin learning
        if msg.text == 'Learn new words':
            functions.create_learning_word_list(users[user_id])
        # if the user click next increase the counter by 1
        elif msg.text == 'next word' and users[user_id].learn_words_counter < (len(users[user_id].learn_words_list)-1):
            users[user_id].learn_words_counter += 1
        # if the user click previous decrease the counter by 1
        elif msg.text == 'previous word' and users[user_id].learn_words_counter > 0:
            users[user_id].learn_words_counter -= 1

        functions.process_learning(msg, users[user_id])

    # for testing
    # if the user begin a test or he/she is in the testing process and he/she didn't finish testing
    elif msg.text == 'Make test' or msg.text == 'Make new test' or \
            (users[user_id].testing_tag == 1 and msg.text != 'finish the test' and msg.text != 'Home 🏠'):
        # if the user begin a test so create a question list and ask a question
        if msg.text == 'Make test' or msg.text == 'Make new test':
            functions.process_first_question(msg, users[user_id])

        # if the user answered a question
        else:
            _, _, eng = users[user_id].test_word_list[users[user_id].test_counter]
            # if answer is right ask new question
            if msg.text == eng:
                functions.process_right_answer(msg, users[user_id])

            # if answer is wrong repeat the same question
            else:

                functions.process_wrong_answer(msg, users[user_id])

    # if it is new user or the user finish learning or finish testing or he/she send any random word
    else:
        functions.show_home_menu(msg, users[user_id])


bot.polling()
