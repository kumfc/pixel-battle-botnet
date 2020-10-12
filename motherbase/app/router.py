from asyncio import ensure_future

from aiohttp import web

from app.interactors.client import ClientInteractor
from app.interactors.tasks import TaskInteractor
from app.interactors.users import UserInteractor
from app.schema import AddUsersSchema, CreateTaskSchema, SetEnabledTaskSchema

from app.schema import ClientStatisticsSchema


def endpoints(database):
    user_interactor = UserInteractor(database.users)
    task_interactor = TaskInteractor(database.tasks)
    client_interactor = ClientInteractor(database.users)

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

    async def clear_all_users(request):
        await client_interactor.clear_all_users()

        return web.json_response({'status': 'success'})

    async def set_enabled_task(request):
        data = await request.json()
        schema_data = SetEnabledTaskSchema(**data)
        await task_interactor.set_enabled(schema_data)

    async def c_send_stats(request):
        data = await request.json()

        client_interactor.print_stat(data['id'], ClientStatisticsSchema(**data['statistics']))

        return web.json_response({'status': 'success'})

    async def c_get_pixels(request):
        data = await request.json()

        pixels = await task_interactor.get_pixels(data['expected_count'])

        return web.json_response({'status': 'success', 'pixels': pixels})

    async def c_get_users(request):
        if not user_interactor.users_loaded:
            return web.json_response({'status': 'failed'})

        data = await request.json()

        users = await client_interactor.get_users_for_client(data['id'])

        return web.json_response({'status': 'success', 'users': users})

    async def c_shutdown(request):
        data = await request.json()

        await client_interactor.take_away_all_users_from_client(data['id'])

        return web.json_response({'status': 'success'})

    return add_users, create_task, clear_all_users, set_enabled_task, c_send_stats, c_get_pixels, c_get_users, c_shutdown
