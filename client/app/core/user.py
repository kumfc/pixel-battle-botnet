import asyncio
import time
import json
import aiohttp
import core.globals as g
import core.sign as sign
import core.logger as log


class User:
    sleep_s = 5
    sign_method = 0

    def __init__(self, ws_url, vk_id):
        self.last_paint_time = 0
        self.vk_id = vk_id
        self.ws_url = ws_url
        self.alive = False
        self.task = None
        self.has_sent_sign = False

        self.start()

    def start(self):
        asyncio.ensure_future(self.connect())

    async def task_listener(self, ws):
        while True:
            if not self.can_draw():
                await asyncio.sleep(self.get_paint_delay())
                continue
            if len(g.c_globals.task_handler) == 0:
                await asyncio.sleep(self.sleep_s)
                continue

            task = g.c_globals.task_handler.pop(0)
            await self.send_pixel(ws, task['x'], task['y'], task['color'])

    async def process_message(self, ws, msg):
        # log.warning('ws_url({}) = {}'.format(self.ws_url, msg))
        try:
            data = json.loads(msg)
        except:
            return

        if 'code' in data['v']:
            try:
                pw = sign.get_sign(data['v']['code'])
            except:
                log.error('%s bruh moment' % self.vk_id)
                await ws.close()
                return

            # log.info('User {} calculated sign {} from {}'.format(self.vk_id, 'R' + str(pw), data['v']['code']))
            try:
                await ws.send_str('R' + str(pw))
            except:
                log.error('User %s disconnected before sign was sent' % self.vk_id)

            self.has_sent_sign = True

    async def send_pixel(self, ws, x, y, color):
        self.last_paint_time = int(time.time())
        await ws.send_bytes(sign.prepare_pixel_packet(x, y, color))

    def get_paint_delay(self):
        return 61 - (int(time.time()) - self.last_paint_time)

    def can_draw(self):
        return (self.get_paint_delay() < 0) and self.alive and self.has_sent_sign

    def is_alive(self):
        return self.alive

    async def connect(self):
        log.info('Connecting to id %s WebSocket' % self.vk_id)
        async with aiohttp.ClientSession() as session:
            while True:
                self.has_sent_sign = False
                try:
                    async with session.ws_connect(self.ws_url) as ws:
                        await self.on_connect(ws)
                except Exception as e:
                    log.error(e)
                    log.error('WebSocket for id %s is unreachable or caused disconnect.' % self.vk_id)
                    log.info('Reconnecting to WebSocket %s in 3 seconds' % self.vk_id)

                try:
                    self.task.cancel()
                except Exception as e:
                    log.error('Internutken upal :(')

                self.alive = False
                await asyncio.sleep(3)

    async def on_connect(self, ws):
        log.info('Successfully connected to id %s WebSocket' % self.vk_id)
        self.task = asyncio.ensure_future(self.task_listener(ws))

        self.alive = True
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                await self.process_message(ws, msg.data)
            elif msg.type == aiohttp.WSMsgType.ERROR:
                log.warning('Got ws error: %s' % msg.data)
                self.alive = False
                return
