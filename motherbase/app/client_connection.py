from asyncio import sleep, ensure_future
from json import dumps, loads

from aiohttp import web

from schema import ClientStatisticsSchema, ClientConnectSchema
from settings import REQUEST_STATISTICS_RATE


class ClientWebsocket:
    def __init__(self, token=None):
        self.total_users = 0
        self.online_users = 0
        self.offline_users = 0
        self.can_draw_users = 0

        self.websocket = None
        self.token = token

    async def send_pixels(self, data):
        await self.websocket.send_json({'command': 'pixels', 'data': list([i.dict() for i in data])})
        print('[+] Sent {} pixels to {}'.format(len(data), self.token))

    async def send_users(self, data):
        await self.websocket.send_json({'command': 'add_users',
                                        'data': list([i.dict(exclude={'token'}) for i in data])})

    def update_statistics(self, statistics: ClientStatisticsSchema):
        self.total_users = statistics.total
        self.online_users = statistics.online
        self.offline_users = statistics.offline
        self.can_draw_users = statistics.can_draw

    async def request_active_users(self):
        while True:
            await self.websocket.send_json({'command': 'statistics'})
            await sleep(REQUEST_STATISTICS_RATE)

    async def handle_connection(self, ws):
        self.websocket = ws
        task = ensure_future(self.request_active_users())

        async for msg in ws:
            if msg.type == web.WSMsgType.text:
                data = loads(msg.data)
                if data['type'] == 'statistics':
                    statistics_data = ClientStatisticsSchema(**data['data'])
                    print('[STATS] ({}) total({}) can_draw({}) online({}) offline({})'.format(self.token,
                                                                                              statistics_data.total,
                                                                                              statistics_data.can_draw,
                                                                                              statistics_data.online,
                                                                                              statistics_data.offline))
                    self.update_statistics(statistics_data)
            else:
                task.cancel()
                break

        return ws
