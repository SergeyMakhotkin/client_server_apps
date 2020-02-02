"""Декораторы, используемые в коде"""

from sys import argv
import logging
import log_config.client_log_config
import log_config.server_log_config
from traceback import format_stack
from inspect import stack

# Определим, какой логгер вызваем
if argv[0].find('my_client') == 1:
    LOGGER = logging.getLogger('app.client')
else:
    LOGGER = logging.getLogger('app.server')


def log(function):
    """функция-декоратор для логирования аргументов, передаваемых декорируемой функции"""

    def log_writter(*args, **kwargs):
        """функция-декоратор (обертка)"""
        func_result = function(*args, **kwargs)
        LOGGER.debug(f'вызывается функция {function.__name__} из модуля {function.__module__}'
                     f'функции переданы параметры {args},{kwargs}'
                     f'функция вернула {func_result}.'
                     f'была вызвана из {format_stack()[0].strip().split()[-1]}')
        return func_result

    return log_writter
