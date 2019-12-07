from asyncio import ensure_future
from typing import List

from aiohttp import web

from interactors.client_connection import ClientConnectionInteractor
from interactors.tasks import TaskInteractor
from interactors.users import UserInteractor
from schema import AddUsersSchema, CreateTaskSchema, SetEnabledTaskSchema


def endpoints(database, clients: List):
    user_interactor = UserInteractor(database.users)
    task_interactor = TaskInteractor(database.tasks, clients)
    client_connection_interactor = ClientConnectionInteractor(clients, database.users)

    ensure_future(task_interactor.process_tasks())
    ensure_future(task_interactor.update_canvas())

    async def add_users(request):
        data = await request.json()
        schema_data = AddUsersSchema(**data)
        await user_interactor.add_users(schema_data)

        return web.json_response({'status': 'success'})

    async def create_task(request):
        data = await request.json()
        schema_data = CreateTaskSchema(**data)
        await task_interactor.create_task(schema_data)

        return web.json_response({'status': 'success'})

    async def get_statistics(request):
        data = await request.json()

        return web.json_response({'status': 'success'})

    async def handle_clients(request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        await client_connection_interactor.handle(ws)

        return ws

    async def clear_all_users(request):
        await client_connection_interactor.clear_all_users()

        return web.json_response({'status': 'success'})

    async def distribute_users_to_clients(request):
        for client in clients:
            await client_connection_interactor.give_users_to_client(client, database.users)

        return web.json_response({'status': 'success'})

    async def set_enabled_task(request):
        data = await request.json()
        schema_data = SetEnabledTaskSchema(**data)
        await task_interactor.set_enabled(schema_data)

    return add_users, create_task, get_statistics, handle_clients, clear_all_users, distribute_users_to_clients, set_enabled_task
