from core.stats import Stats


def init():
    global c_globals
    c_globals = ClientGlobals()


class ClientGlobals:

    def __init__(self):
        self.bruh_moment = True
        self.task_handler = list()
        self.user_handler = list()
        self.stats = Stats()
