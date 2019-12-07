from client_connection import ClientWebsocket
from aiohttp import web
import json
from schema import ClientConnectSchema, User
from asyncio import sleep, ensure_future
from settings import CLIENT_DISCONNECT_TIMEOUT, MAX_USERS_PER_CLIENT


class ClientConnectionInteractor:
    def __init__(self, clients, users_database):
        self.clients = clients
        self.users_database = users_database

    async def handle(self, ws):
        msg = await ws.receive()
        if msg.type == web.WSMsgType.text:
            data = json.loads(msg.data)
            if data['type'] == 'connect':
                connect_data = ClientConnectSchema(**data['data'])
                token_client = self.get_client_by_token(connect_data.token)
                if token_client is None:
                    token_client = ClientWebsocket(connect_data.token)
                    self.clients.append(token_client)
                else:
                    if hasattr(token_client, 'coroutine'):
                        token_client.coroutine.cancel()
                        token_client.coroutine = None
                    else:
                        token_client = ClientWebsocket(connect_data.token)
                        self.clients.append(token_client)
                print('[+] Client with token ({}) connected!'.format(token_client.token))
                await token_client.handle_connection(ws)

                token_client.websocket = None
                token_client.coroutine = ensure_future(self.wait_to_reconnect(token_client))

    def get_client_by_token(self, token):
        for i in self.clients:
            if i.token == token:
                return i
        return None

    async def wait_to_reconnect(self, token_client):
        await sleep(CLIENT_DISCONNECT_TIMEOUT)
        token_client.coroutine = None
        self.clients.remove(token_client)
        await self.take_away_all_users_from_client(token_client)

    async def take_away_all_users_from_client(self, client):
        await self.users_database.update_many(filter={'client': client.token}, update={"$set": {'client': None}})

    async def give_users_to_client(self, client, users_database):
        data = []
        clients_users = await users_database.count_documents({'client': client.token})
        needed_users = max(0, MAX_USERS_PER_CLIENT - clients_users)
        free_users = users_database.find({'client': None}).limit(needed_users)
        async for i in free_users:
            await users_database.update_one(filter={'_id': i['_id']}, update={"$set": {'client': client.token}})
            data.append(User(**i))

        await client.send_users(data)

    async def clear_all_users(self):
        await self.users_database.update_many(filter={}, update={"$set": {'client': None}})
