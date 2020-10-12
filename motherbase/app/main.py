from asyncio import ensure_future
from collections import namedtuple
from os import environ

from aiohttp import web
from motor import motor_asyncio

from app.router import endpoints

DatabaseInjection = namedtuple('DatabaseInjection', ['users', 'tasks'])


def init_database():
    client = motor_asyncio.AsyncIOMotorClient(environ['DATABASE_URL'])
    database = client['pixel-battle-botnet']
    database_injection = DatabaseInjection(database.users, database.tasks)

    return database_injection


async def startup(database):
    await database.users.update_many(filter={}, update={"$set": {'client': None}})


def main():
    db = init_database()
    add_users, create_task, clear_all_users, set_enabled_task, c_send_stats, c_get_pixels, c_get_users, c_shutdown = endpoints(db)
    ensure_future(startup(db))

    webapp = web.Application(client_max_size=10 ** 7)
    webapp.add_routes([web.post('/add-users', add_users),
                       web.post('/create-task', create_task),
                       web.post('/clear-users', clear_all_users),
                       web.post('/enable-task', set_enabled_task),
                       web.post('/c/send-stats', c_send_stats),
                       web.post('/c/get-pixels', c_get_pixels),
                       web.post('/c/get-users', c_get_users),
                       web.post('/c/shutdown', c_shutdown)])
    web.run_app(webapp, port=1337)
