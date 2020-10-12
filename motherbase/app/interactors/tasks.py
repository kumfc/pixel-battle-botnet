import io
from asyncio import sleep
from datetime import datetime
from random import shuffle

import aiohttp
from PIL import Image

from app.schema import CreateTaskSchema, Pixel, SetEnabledTaskSchema
from app.settings import CANVAS_UPDATE_TIME

color_map = ["FFFFFF", "C2C2C2", "858585", "474747", "000000", "3AAFFF", "71AAEB", "4A76A8", "074BF3",
             "5E30EB", "FF6C5B", "FE2500", "FF218B", "99244F", "4D2C9C", "FFCF4A", "FEB43F", "FE8648",
             "FF5B36", "DA5100", "94E044", "5CBF0D", "C3D117", "FCC700", "D38301"]


class TaskInteractor:
    def __init__(self, database_tasks):
        self.database_tasks = database_tasks
        self.current_canvas = None
        self.pixel_pool = list()

    async def create_task(self, data: CreateTaskSchema):
        await self.database_tasks.insert_one(
            {'name': data.name, 'is_enabled': data.is_enabled, 'creation_time': datetime.now(),
             'pixels': list([i.dict() for i in data.pixels])}
        )

    async def update_pixel_pool(self):
        try:
            self.pixel_pool = list()
            async for task in self.database_tasks.find():
                if not task['is_enabled']:
                    continue

                pixels = []
                for i in task['pixels']:
                    pixels.append(i)
                #shuffle(pixels)
                pixels.reverse()

                for current_pixel in pixels:
                    pixel = Pixel(**current_pixel)
                    if not await self.check_pixel_painted(pixel.color, pixel.x, pixel.y):
                        self.pixel_pool.append(pixel.dict())
        except IndexError:
            print('IndexError - Broken task!')

    async def get_pixels(self, cnt_needed):
        pixel_list = list()
        for pixel in self.pixel_pool:
            pixel_list.append(pixel)
            self.pixel_pool.remove(pixel)
            if len(pixel_list) >= cnt_needed:
                return pixel_list
        return pixel_list

    async def update_canvas(self):
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get('https://dev.umfc.xyz/pixel.png') as resp:
                        im = Image.open(io.BytesIO(await resp.read()))
                        self.current_canvas = im.load()
            except Exception as exc:
                print('EXCEPTION IN UPDATE CANVAS LOOP', exc)
            if len(self.pixel_pool) == 0:
                await self.update_pixel_pool()

            await sleep(CANVAS_UPDATE_TIME)

    async def check_pixel_painted(self, color, x, y):
        if self.current_canvas is None:
            return False

        r, g, b = map(int, self.current_canvas[x, y])
        c = '{:02X}{:02X}{:02X}'.format(r, g, b)

        return color_map.index(c) == color

    async def set_enabled(self, data: SetEnabledTaskSchema):
        await self.database_tasks.update_many(filter={'name': data.name},
                                              update={"$set": {'is_enabled': data.is_enabled}})
