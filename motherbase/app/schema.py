from random import randint
from typing import List

from pydantic import BaseModel, validator


class User(BaseModel):
    vk_id: int
    vk_token: str
    vk_websocket: str
    client: str = None
    delay: int = -1

    @validator('delay', pre=True, always=True)
    def set_delay(cls, v):
        result = v
        if result == -1:
            result = randint(0, 100)

        return result


class AddUsersSchema(BaseModel):
    users: List[User]


class Pixel(BaseModel):
    x: int
    y: int
    color: int


class CreateTaskSchema(BaseModel):
    name: str
    is_enabled: bool = True
    pixels: List[Pixel]


class ClientStatisticsSchema(BaseModel):
    total: int
    online: int
    offline: int
    can_draw: int


class ClientConnectSchema(BaseModel):
    token: str


class SetEnabledTaskSchema(BaseModel):
    name: str
    is_enabled: bool
