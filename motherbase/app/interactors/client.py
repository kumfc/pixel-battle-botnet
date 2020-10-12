import asyncio

from app.schema import User, ClientStatisticsSchema
from app.settings import MAX_USERS_PER_CLIENT


class ClientInteractor:
    def __init__(self, users_database):
        self.users_database = users_database
        self._sultan = False  # my protiv gonok

    @staticmethod
    def print_stat(client_token, stat: ClientStatisticsSchema):
        print(f'[{client_token}]\nTotal: {stat.total}\nOnline: {stat.online}\nOffline: {stat.offline}\nCan draw: {stat.can_draw}')

    async def take_away_all_users_from_client(self, client_token):
        await self.users_database.update_many(filter={'client': client_token}, update={"$set": {'client': None}})

    async def get_users_for_client(self, client_token):
        while self._sultan:
            await asyncio.sleep(1)
        self._sultan = True
        data = []
        clients_users = await self.users_database.count_documents({'client': client_token})
        if clients_users > 0:
            await self.take_away_all_users_from_client(client_token)
        needed_users = MAX_USERS_PER_CLIENT
        free_users = self.users_database.find({'client': None}).limit(needed_users)

        async for i in free_users:
            await self.users_database.update_one(filter={'_id': i['_id']}, update={"$set": {'client': client_token}})
            data.append(User(**i).dict())

        print(f'Sending {len(data)} users to {client_token}')
        self._sultan = False
        return data

    async def clear_all_users(self):
        await self.users_database.update_many(filter={}, update={"$set": {'client': None}})
