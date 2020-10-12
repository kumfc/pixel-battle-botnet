from app.main import g


class Stats:

    def __init__(self):
        self.total = 0
        self.online = 0
        self.offline = 0
        self.can_draw = 0

    def get_total_users(self):
        return self.total

    def get_online_users(self):
        return self.online

    def get_offline_users(self):
        return self.offline

    def get_can_draw_users(self):
        return self.can_draw

    def count_online(self):
        k = 0
        for user in g.user_handler:
            if user.is_alive():
                k += 1

        self.total = len(g.user_handler)
        self.online = k
        self.offline = self.total - k

    def count_can_draw(self):
        k = 0
        for user in g.user_handler:
            if user.can_draw():
                k += 1

        self.can_draw = k

    def update_stats(self):
        self.count_online()
        self.count_can_draw()

    def get_stats_assoc(self):
        self.update_stats()
        return {'total': self.total, 'online': self.online, 'offline': self.offline, 'can_draw': self.can_draw}
