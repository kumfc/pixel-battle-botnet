import asyncio
import json
import tracemalloc
from asyncio import ensure_future
from random import randint, shuffle

from app.core.globals import ClientGlobals

g = ClientGlobals()

from app.core.user import User
from app.core.stats import Stats

import app.utils.logger as log
import app.config as config
from app.core.mother_base import MotherBase

mother_api = 'http://motherbase:1337'


async def main():
    g.stats = Stats()

    if config.mode == 1:
        proxy_f = '/app/proxies.list'
    else:
        proxy_f = 'proxies.list'

    with open(proxy_f) as f:
        g.proxy_list = f.read().splitlines()

    if config.mode == 1:
        matb = MotherBase(mother_api)
        try:
            ensure_future(matb.get_users())
            ensure_future(matb.run_interaction_loop())

            while True:
                await asyncio.sleep(1)
        except Exception as e:
            log.error(f'Main thread exception: {e}')
        finally:
            await matb.shutdown()
    elif config.mode == 2:
        with open(f'../../core/db/{config.single_db}') as f:
            users = json.loads(f.read())
        for user in users:
            g.user_handler.append(User(user['url'], user['user_id'], randint(1, 3)))

        with open(f'../../core/tasks/{config.single_task}') as f:
            tasks = json.loads(f.read())
            # shuffle(tasks)
            g.task_handler.extend(tasks)

        while True:
            tracemalloc.start()
            await asyncio.sleep(120)
            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics('lineno')

            print("[ Top 10 ]")
            for stat in top_stats[:10]:
                print(stat)
    else:
        log.error('Unknown launch mode.')
