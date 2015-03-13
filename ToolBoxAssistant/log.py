# -*- coding: utf-8 -*-
from logging import Formatter, StreamHandler, getLogger, DEBUG

from ToolBoxAssistant.helpers import Color

LOG_FORMAT = '[%(levelname)s] %(message)s'


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
