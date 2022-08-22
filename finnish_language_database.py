import sqlite3


# —————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————

CREATE_CUSTOMER_TABLE = 'CREATE TABLE IF NOT EXISTS "{}" (word_id INTEGER ,repeating_amount INTEGER, word_learned INTEGER);'
CHECK_IF_TABLE_IS_EMPTY = 'SELECT COUNT(*) from "{}" '
CHOOSE_NEW_WORDS = 'SELECT id, finnish, english  FROM finish_language_table LIMIT ? OFFSET ?;'
INSERT_WORD_TO_USER = 'INSERT INTO "{}"  VALUES(?, ?, ?);'
GET_THE_LAST_ROW = 'SELECT * FROM "{}" WHERE word_id=(SELECT max(word_id) FROM "{}");'
CHOOSE_USER_RANDOM_WORDS_ID = 'SELECT word_id FROM "{}" ORDER BY RANDOM() LIMIT "{}";'
GET_WORDS = 'SELECT finnish, english FROM finish_language_table WHERE id = ?;'

# —————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————


def connect():
    return sqlite3.connect("db_finish_language.db")


def create_customer_table(connection, customer_ID):
    with connection:
        connection.execute(CREATE_CUSTOMER_TABLE.format(customer_ID))


def check_if_table_is_empty(connection, customer_ID):
    with connection:
        return connection.execute(CHECK_IF_TABLE_IS_EMPTY.format(customer_ID)).fetchall()


def choose_new_words(connection, rows_number, begin_from):
    with connection:
        return connection.execute(CHOOSE_NEW_WORDS, ((rows_number), (begin_from))).fetchall()


def insert_word_to_user(connection, customer_ID, word_ID):
    with connection:
        connection.execute(INSERT_WORD_TO_USER.format(
            customer_ID), (word_ID, 1, 0))


def get_the_last_row(connection, customer_ID):
    with connection:
        return connection.execute(GET_THE_LAST_ROW.format(customer_ID,  customer_ID)).fetchone()


def choose_random_user_words(connection, customer_ID, Number_of_words):
    with connection:
        words_list = []
        random_ids = connection.execute(CHOOSE_USER_RANDOM_WORDS_ID.format(
            customer_ID, Number_of_words)).fetchall()
        for id in random_ids:
            fin, eng = connection.execute(GET_WORDS, (id)).fetchone()
            words_list.append((id, fin, eng))
        return words_list
