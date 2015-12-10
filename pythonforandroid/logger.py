
import logging
from sys import stdout, stderr, platform
from collections import defaultdict
from colorama import Style as Colo_Style, Fore as Colo_Fore

class LevelDifferentiatingFormatter(logging.Formatter):
    def format(self, record):
        if record.levelno > 30:
            record.msg = '{}{}[ERROR]{}{}:   '.format(
                Err_Style.BRIGHT, Err_Fore.RED, Err_Fore.RESET,
                Err_Style.RESET_ALL) + record.msg
        elif record.levelno > 20:
            record.msg = '{}{}[WARNING]{}{}: '.format(
                Err_Style.BRIGHT, Err_Fore.RED, Err_Fore.RESET,
                Err_Style.RESET_ALL) + record.msg
        elif record.levelno > 10:
            record.msg = '{}[INFO]{}:    '.format(
                Err_Style.BRIGHT, Err_Style.RESET_ALL) + record.msg
        else:
            record.msg = '{}{}[DEBUG]{}{}:   '.format(
                Err_Style.BRIGHT, Err_Fore.LIGHTBLACK_EX, Err_Fore.RESET,
                Err_Style.RESET_ALL) + record.msg
        return super(LevelDifferentiatingFormatter, self).format(record)

logger = logging.getLogger('p4a')
if not hasattr(logger, 'touched'):  # Necessary as importlib reloads
                                    # this, which would add a second
                                    # handler and reset the level
    logger.setLevel(logging.INFO)
    logger.touched = True
    ch = logging.StreamHandler(stderr)
    formatter = LevelDifferentiatingFormatter('%(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
info = logger.info
debug = logger.debug
warning = logger.warning
error = logger.error

class colorama_shim(object):

    def __init__(self):
        self._dict = defaultdict(str)

    def __getattr__(self, key):
        return self._dict[key]

Null_Style = Null_Fore = colorama_shim()

if stdout.isatty():
    Out_Style = Colo_Style
    Out_Fore = Colo_Fore
else:
    Out_Style = Null_Style
    Out_Fore = Null_Fore

if stderr.isatty():
    Err_Style = Colo_Style
    Err_Fore = Colo_Fore
else:
    Err_Style = Null_Style
    Err_Fore = Null_Fore
