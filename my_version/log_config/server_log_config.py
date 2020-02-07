"""Конфигурация логгера для серверного приложения"""

from logging import getLogger, StreamHandler, Formatter, DEBUG
import os
import sys
from logging.handlers import TimedRotatingFileHandler
from common.settings import SERV_LOGGING_LEVEL

# Создаем логгер
LOG = getLogger('app.server')

# Создаем формировщик логов
SERV_FORMATTER_D = Formatter('%(asctime)s %(levelname)s %(filename)s %(funcName)s %(message)s')
SERV_FORMATTER_I = Formatter(
    '%(asctime)s %(levelname)s %(filename)s %(message)s')

# Настройки пути к файлу логов
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, '..', 'log', 'server.log')

# Создаем обработчики для логгера
STEAM_HANDLER = StreamHandler(sys.stderr)
STEAM_HANDLER.setFormatter(SERV_FORMATTER_D)
STEAM_HANDLER.setLevel(DEBUG)
FILE_HANDLER = TimedRotatingFileHandler(PATH, encoding='utf-8', interval=1, when='D')
FILE_HANDLER.setFormatter(SERV_FORMATTER_D)

# Настраиваем логгер
LOG.addHandler(STEAM_HANDLER)
LOG.addHandler(FILE_HANDLER)
LOG.setLevel(SERV_LOGGING_LEVEL)

# отладка конфига логгера
if __name__ == '__main__':
    LOG.critical('Критическая ошибка')
    LOG.error('Ошибка')
    LOG.warning('Предупреждение')
    LOG.info('Инфо')
    LOG.debug('дебаг')
