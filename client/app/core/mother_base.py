import asyncio
import aiohttp
import json
import uuid
import core.globals as g
import core.logger as log
from core.user import User


class MotherBase:

    def __init__(self, mother_ws):
        self.alive = False
        self.ws_url = mother_ws
        self.id = str(uuid.uuid4())

        self.start()

    def start(self):
        asyncio.run(self.connect())

    async def process_message(self, ws, text):
        try:
            data = json.loads(text)
        except:
            return log.warning('Unexpected stuff was thrown from mother base :p')

        if data['command'] == 'statistics':
            response = {'type': 'statistics', 'data': g.c_globals.stats.get_stats_assoc()}
            log.debug('MotherBase requested stats: %s' % str(response))
            await ws.send_json(response)
        elif data['command'] == 'pixels' and 'data' in data:
            log.info('Received %s tasks from mother base.' % len(data['data']))
            g.c_globals.task_handler.extend(data['data'])
            log.info('%s total tasks to proceed' % len(g.c_globals.task_handler))
        elif data['command'] == 'add_users' and 'data' in data:
            log.info("Received %s users from mother base." % len(data['data']))
            for user in data['data']:
                g.c_globals.user_handler.append(User(user['vk_websocket'], user['vk_id']))

    async def connect(self):
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    async with session.ws_connect(self.ws_url) as ws:
                        await self.on_connect(ws)
                except aiohttp.ClientConnectorError as e:
                    log.error('MotherBase caused disconnect.')
                    log.info('Reconnecting to MotherBase in 1 second')

                await asyncio.sleep(1)

    async def make_handshake(self, ws):
        c_info = {'type': 'connect', 'data': {'token': self.id}}
        await ws.send_json(c_info)

    async def on_connect(self, ws):
        self.alive = True
        await self.make_handshake(ws)

        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                await self.process_message(ws, msg.data)
            elif msg.type == aiohttp.WSMsgType.ERROR:
                self.alive = False
                break
