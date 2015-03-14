# -*- coding: utf-8 -*-
import os
from logging import Formatter, StreamHandler, getLogger, DEBUG
from tempfile import mkstemp

LOG_FORMAT = '[%(levelname)s] %(message)s'


class Color(object):
    BLUE = '\033[0;34m'
    BLUEBOLD = '\033[1;34m'
    GREEN = '\033[0;32m'
    GREENBOLD = '\033[1;32m'
    RED = '\033[0;31m'
    REDBOLD = '\033[1;31m'
    END = '\033[0m'


class ColorFormatter(Formatter):
    """
    A logging formatter that displays the loglevel with colors.
    """
    _colors_map = {
        'DEBUG': Color.GREENBOLD,
        'INFO': Color.BLUEBOLD,
        'WARNING': Color.RED,
        'ERROR': Color.REDBOLD
    }

    def format(self, record):
        if record.levelname in self._colors_map:
            record.levelname = '%s%s%s' % (
                self._colors_map[record.levelname],
                record.levelname,
                Color.END
            )
        return super(ColorFormatter, self).format(record)


def log_to_file(data):
    fd, tmpname = mkstemp(prefix='tba-', suffix='.txt')
    os.write(fd, data)
    os.close(fd)
    return tmpname


def get_logger(name):
    formatter = ColorFormatter(LOG_FORMAT)
    handler = StreamHandler()
    handler.setFormatter(formatter)
    logger = getLogger(name)
    logger.setLevel(DEBUG)
    logger.addHandler(handler)
    return logger


logger = get_logger('tba')
