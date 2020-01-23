"""unit-тесты для серверного скрипта"""

import sys
import os
import unittest
from my_server import process_client_message
from my_package.settings import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE

sys.path.append(os.path.join(os.getcwd(), '..'))


class TestServer(unittest.TestCase):
    """тестируем функцию ответа клиенту.
    для функции process_client_message в сообщении от клиента можем проверить
    наличие требуемых ключей, и некоторые значения по этим ключам
    """
    err_response = {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }
    ok_response = {RESPONSE: 200}

    def test_action_field_in_msg(self):
        """Ошибка если нет действия"""
        self.assertEqual(process_client_message(
            {TIME: '1.1', USER: {ACCOUNT_NAME: 'Guest'}}), self.err_response)

    def test_action_wrong_value_in_msg(self):
        """Ошибка если неизвестное действие"""
        self.assertEqual(process_client_message(
            {ACTION: 'Wrong', TIME: '1.1', USER: {ACCOUNT_NAME: 'Guest'}}), self.err_response)

    def test_no_time_in_msg(self):
        """Ошибка, если  запрос не содержит штампа времени"""
        self.assertEqual(process_client_message(
            {ACTION: PRESENCE, USER: {ACCOUNT_NAME: 'Guest'}}), self.err_response)

    def test_no_user_in_msg(self):
        """Ошибка - нет пользователя"""
        self.assertEqual(process_client_message(
            {ACTION: PRESENCE, TIME: '1.1'}), self.err_response)

    def test_unknown_user_in_msg(self):
        """Ошибка - не Guest"""
        self.assertEqual(process_client_message({ACTION: PRESENCE, TIME: 1.1, USER: {
            ACCOUNT_NAME: 'Guest1'}}), self.err_response)

    def test_ok_check_in_msg(self):
        """Корректный запрос"""
        self.assertEqual(process_client_message(
            {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}}), self.ok_response)


if __name__ == '__main__':
    unittest.main()
