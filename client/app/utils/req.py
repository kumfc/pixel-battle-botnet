import json

import aiohttp
import app.utils.logger as log


async def get(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                res = await resp.text()
                return json.loads(res)
    except Exception as e:
        log.error(f'Exception in _.get: {e}')


async def post(url, data=None):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers={'Authorization': 'Basic YWxsbzp3RmZMckxxYg=='}) as resp:
                res = await resp.text()
                return json.loads(res)
    except Exception as e:
        log.error(f'Exception in _.post: {e}')
