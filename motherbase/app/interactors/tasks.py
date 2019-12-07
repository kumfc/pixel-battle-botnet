from schema import CreateTaskSchema, Pixel, SetEnabledTaskSchema
from datetime import datetime
from asyncio import sleep
from settings import PIXELS_TIMEOUT, CANVAS_UPDATE_TIME
from PIL import Image
import aiohttp
import io

color_map = ["FFFFFF", "C2C2C2", "858585", "474747", "000000", "3AAFFF", "71AAEB", "4A76A8", "074BF3",
             "5E30EB", "FF6C5B", "FE2500", "FF218B", "99244F", "4D2C9C", "FFCF4A", "FEB43F", "FE8648",
             "FF5B36", "DA5100", "94E044", "5CBF0D", "C3D117", "FCC700", "D38301"]


class TaskInteractor:
    def __init__(self, database_tasks, clients):
        self.database_tasks = database_tasks
        self.clients = clients
        self.current_canvas = None

    async def create_task(self, data: CreateTaskSchema):
        await self.database_tasks.insert_one(
            {'name': data.name, 'is_enabled': data.is_enabled, 'creation_time': datetime.now(),
             'pixels': list([i.dict() for i in data.pixels])}
        )

    async def process_tasks(self):
        current_client = 0
        current_client_data = []

        while True:
            async for task in self.database_tasks.find():
                for i in task['pixels']:
                    while len(self.clients) == 0:
                        await sleep(PIXELS_TIMEOUT)

                    if not task['is_enabled']:
                        break

                    while True:
                        try:
                            if len(current_client_data) < self.clients[current_client].can_draw_users:
                                pixel = Pixel(**i)
                                if not await self.check_pixel_painted(pixel.color, pixel.x, pixel.y):
                                    current_client_data.append(pixel)
                                break
                            else:
                                if len(current_client_data) > 0:
                                    await self.clients[current_client].send_pixels(current_client_data)
                                current_client += 1

                                if current_client >= len(self.clients):
                                    await sleep(PIXELS_TIMEOUT)
                                    current_client = 0

                                current_client_data = []
                        except Exception as exc:
                            print('EXCEPTION IN TASK LOOP', exc)

            await sleep(PIXELS_TIMEOUT)

    async def update_canvas(self):
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get('https://dev.umfc.xyz/pixel.png') as resp:
                        im = Image.open(io.BytesIO(await resp.read()))
                        self.current_canvas = im.load()
            except Exception as exc:
                print('EXCEPTION IN UPDATE CANVAS LOOP', exc)

            await sleep(CANVAS_UPDATE_TIME)

    async def check_pixel_painted(self, color, x, y):
        if self.current_canvas is None:
            return False

        r, g, b = map(int, self.current_canvas[x, y])
        c = '{:02X}{:02X}{:02X}'.format(r, g, b)

        return color_map.index(c) == color

    async def set_enabled(self, data: SetEnabledTaskSchema):
        await self.database_tasks.update_many(filter={'name': data.name}, update={"$set": {'is_enabled': data.is_enabled}})
