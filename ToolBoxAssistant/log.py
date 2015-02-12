# -*- coding: utf-8 -*-
from logging import Formatter, StreamHandler, getLogger, DEBUG

LOG_FORMAT = '[%(levelname)s] %(message)s'


class ColorFormatter(Formatter):
    """
    A logging formatter that displays the loglevel with colors.
    """
    _colors_map = {
        'DEBUG': '\033[1;32m',
        'INFO': '\033[1;34m',
        'WARNING': '\033[0;31m',
        'ERROR': '\033[1;31m',
    }

    def format(self, record):
        if record.levelname in self._colors_map:
            record.levelname = '%s%s\033[0;0m' % (
                self._colors_map[record.levelname],
                record.levelname
            )
        return super(ColorFormatter, self).format(record)


def get_logger(name):
    formatter = ColorFormatter(LOG_FORMAT)
    handler = StreamHandler()
    handler.setFormatter(formatter)
    logger = getLogger(name)
    logger.setLevel(DEBUG)
    logger.addHandler(handler)
    return logger
