import asyncio
import time
import json
import random
import aiohttp

from app import config
from app.main import g
import app.core.sign as sign
import app.utils.logger as log


class User:
    sleep_s = 5
    sign_method = 0

    def __init__(self, ws_url, vk_id, delay):
        self.last_paint_time = 0
        self.vk_id = vk_id
        self.ws_url = ws_url
        self.alive = False
        self.task = None
        self.has_sent_sign = True
        self.delay = delay
        self.bruh = False
        self.msg = ''

        self.start()

    def start(self):
        asyncio.ensure_future(self.connect())

    async def task_listener(self, ws):
        while True:
            if not self.can_draw():
                await asyncio.sleep(self.get_paint_delay())
                continue
            if len(g.task_handler) == 0:
                await asyncio.sleep(self.sleep_s)
                continue

            task = g.task_handler.pop(0)
            await self.send_pixel(ws, task['x'], task['y'], task['color'])

    async def process_message(self, ws, msg):
        # log.debug(f'ws_onmessage: {msg}')
        self.msg = msg
        # if 'pong' not in msg:
        #     await ws.send_str('ping')
        if msg == 'BAD_CLIENT_BAN':
            log.error(f'USER {self.vk_id} RECEIVED BAD_CLIENT_BAN!')
            self.bruh = True
            g.bruh_moment += 1
            return
        try:
            data = json.loads(msg)
        except:
            return

        if 'v' in data and type(data['v']) == int:
            return  # спасибо иванн недвезкии

        if 'code' in data['v']:
            try:
                pw = sign.get_sign(data['v']['code'])
            except:
                log.error(f'{self.vk_id} bruh moment')
                await ws.close()
                return

            try:
                await ws.send_str('R' + str(pw))
            except:
                log.error(f'User {self.vk_id} disconnected before sign was sent')

            self.has_sent_sign = True

    async def send_pixel(self, ws, x, y, color):
        self.last_paint_time = int(time.time())
        await ws.send_bytes(sign.prepare_pixel_packet(x, y, color))

    def get_paint_delay(self):
        return config.time_delay_between_paint - (int(time.time()) - self.last_paint_time)

    def can_draw(self):
        return (self.get_paint_delay() < 0) and self.alive and self.has_sent_sign

    def is_alive(self):
        return self.alive

    async def connect(self):
        await asyncio.sleep(self.delay)
        async with aiohttp.ClientSession() as session:
            while True:
                self.has_sent_sign = True
                try:
                    if config.use_proxy:
                        host, port, username, password = random.choice(g.proxy_list).split(':')
                        proxy = f'http://{username}:{password}@{host}:{port}'
                    else:
                        proxy = ''

                    async with session.ws_connect(self.ws_url, proxy=proxy) as ws:
                        await self.on_connect(ws)
                #except TimeoutError:
                #    ...
                except Exception as e:
                    log.error(f'ID({self.vk_id}) disconnected. Reconnecting.\nLast message: {self.msg}\nException: {e}')

                try:
                    self.task.cancel()
                except Exception as e:
                    log.error('Internet problems.')

                self.alive = False
                if self.bruh:
                    return
                await asyncio.sleep(3)

    async def on_connect(self, ws):
        log.info(f'Successfully connected to id {self.vk_id} WebSocket')
        self.task = asyncio.ensure_future(self.task_listener(ws))

        self.alive = True
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                await self.process_message(ws, msg.data)
            elif msg.type == aiohttp.WSMsgType.ERROR:
                log.warning(f'Got ws error: {msg.data}')
                self.alive = False
                return
