from asyncio import ensure_future
from collections import namedtuple
from os import environ

from aiohttp import web
from motor import motor_asyncio

from router import endpoints

DatabaseInjection = namedtuple('DatabaseInjection', ['users', 'tasks'])


def init_database():
    client = motor_asyncio.AsyncIOMotorClient(environ['DATABASE_URL'])
    database = client['pixel-battle-botnet']
    database_injection = DatabaseInjection(database.users, database.tasks)

    return database_injection


async def startup(database):
    await database.users.update_many(filter={}, update={"$set": {'client': None}})


if __name__ == '__main__':
    clients = []
    db = init_database()
    add_users, create_task, get_statistics, handle_clients, clear_all_users, distribute_users_to_clients, set_enabled_task = endpoints(db, clients)
    ensure_future(startup(db))

    app = web.Application(client_max_size=10**7)
    app.add_routes([web.post('/add-users', add_users),
                    web.post('/create-task', create_task),
                    web.post('/clear-users', clear_all_users),
                    web.post('/distribute-users', distribute_users_to_clients),
                    web.post('/enable-task', set_enabled_task),
                    web.get('/ws', handle_clients)])
    web.run_app(app, port=1337)
