import socket
import time
import asyncio
import json
import uuid
from app.main import g
import app.utils.logger as log
import app.utils.req as r
from app.core.user import User


class MotherBase:
    def __init__(self, mother_url):
        self.alive = False
        self.url = mother_url
        # self.id = str(uuid.uuid4())
        self.id = socket.gethostname()

    async def run_interaction_loop(self):
        while True:
            if len(g.task_handler) == 0:
                await self.get_tasks()
            if int(time.time()) % 20 == 0:
                await self.send_stats()
            await asyncio.sleep(1)

    async def shutdown(self):
        log.warning(f'Client shutting down...')
        await r.post(f'{self.url}/c/shutdown', data={'id': self.id})

    async def get_tasks(self):
        can_run = int(g.stats.get_stats_assoc()['can_draw'])
        data = await r.post(f'{self.url}/c/get-pixels', data={'id': self.id, 'expected_count': can_run})

        if data is None:
            return

        if 'pixels' in data and len(data['pixels']) > 0:
            g.task_handler.extend(data['pixels'])
            log.info(f'Retrieved {len(data["pixels"])} tasks from the base.')

    async def send_stats(self):
        stat = g.stats.get_stats_assoc()  # maybe g.bruh_moment
        await r.post(f'{self.url}/c/send-stats', data={'id': self.id, 'statistics': stat})

    async def get_users(self):
        while True:
            data = await r.post(f'{self.url}/c/get-users', data={'id': self.id})

            if data is None:
                continue

            if data['status'] == 'success' and len(data['users']) > 0:
                break
            await asyncio.sleep(15)

        users = data['users']
        log.info(f'Retrieved {len(users)} users from the base.')
        for user in users:
            g.user_handler.append(User(user['vk_websocket'], user['vk_id'], user['delay']))
