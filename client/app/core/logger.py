import datetime


def ts():
    return str(datetime.datetime.now().strftime('%I:%M:%S'))


def log_print(text, type):
    print('[{}][{}] {}'.format(ts(), type, text))


def error(text):
    log_print(text, 'ERROR')


def info(text):
    log_print(text, 'INFO')


def warning(text):
    log_print(text, 'WARNING')


def debug(text):
    log_print(text, 'DEBUG')
