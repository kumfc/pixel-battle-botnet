from app.schema import AddUsersSchema


class UserInteractor:
    def __init__(self, database_users):
        self.database_users = database_users
        self.users_loaded = False

    async def add_users(self, data: AddUsersSchema):
        self.users_loaded = True
        await self.database_users.insert_many(list([i.dict() for i in data.users]))
