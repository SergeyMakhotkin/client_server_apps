"""unit-тесты для клиентского скрипта"""
import sys
import os
import unittest
from my_client import generate_presence_msg, process_server_response
from common.settings import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE

sys.path.append(os.path.join(os.getcwd(), '..'))
"""добавляем в системную переменную path родительскую дирректорию для поиска модулей"""


class TestClass(unittest.TestCase):
    """
    Создаем класс для тестирования (наследуем от TestCase)
    """

    def test_presense_msg(self):
        """тест фформата запроса к серверу"""
        t_msg = generate_presence_msg()
        t_msg[TIME] = 1.1
        """принудительно меняем значение для TIME"""
        self.assertEqual(
            t_msg, {
                ACTION: PRESENCE, TIME: 1.1, USER: {
                    ACCOUNT_NAME: 'Guest'}})

    """проверяем поведение обработчика ответа от сервера:
    1) ответ 200
    2) ответ 400"""

    def test_response_200(self):
        self.assertEqual(process_server_response({RESPONSE: 200}), '200 : OK')
        """проверяем, что если сервер ответил "200",
        то process_server_ans вернет строку '200 : OK' """

    def test_response_400(self):
        self.assertEqual(process_server_response(
            {RESPONSE: 400, ERROR: 'request error'}), '400 : request error')

    def test_no_server_response(self):
        self.assertRaises(
            ValueError, process_server_response, {
                ERROR: 'главное ключ ERROR? сообщение м.б. любое??'})


if __name__ == '__main__':
    unittest.main()
