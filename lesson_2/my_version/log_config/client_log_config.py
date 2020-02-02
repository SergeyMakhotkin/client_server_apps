"""Конфигурация логгера для клиентского приложения"""

import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler
from common.settings import CLIENT_LOGGING_LEVEL



# Создаем формировщик логов
CLIENT_FORMATTER_D = logging.Formatter(
    '%(asctime)s %(levelname)s %(filename)s %(funcName)s %(message)s')
CLIENT_FORMATTER_I = logging.Formatter(
    '%(asctime)s %(levelname)s %(filename)s %(message)s')

# Настройки пути к файлу логов
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, '..', 'log', 'client.log')

# Создаем обработчики для логгера
STEAM_HANDLER = logging.StreamHandler(sys.stderr)
STEAM_HANDLER.setFormatter(CLIENT_FORMATTER_D)
STEAM_HANDLER.setLevel(logging.DEBUG)
# FILE_HANDLER = TimedRotatingFileHandler(
#     PATH, encoding='utf-8', interval=1, when='D')
FILE_HANDLER = logging.FileHandler(PATH, encoding='utf-8')
FILE_HANDLER.setFormatter(CLIENT_FORMATTER_D)
FILE_HANDLER.setLevel(logging.DEBUG)

# Настраиваем логгер
# Создаем логгер
LOG = logging.getLogger('app.client')
LOG.addHandler(FILE_HANDLER)
LOG.addHandler(STEAM_HANDLER)
LOG.setLevel(CLIENT_LOGGING_LEVEL)

# отладка конфига логгера
if __name__ == '__main__':
    LOG.critical('Критическая ошибка')
    LOG.error('Ошибка')
    LOG.warning('Предупреждение')
    LOG.info('Инфо')
    LOG.debug('дебаг')
