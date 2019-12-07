from schema import AddUsersSchema


class UserInteractor:
    def __init__(self, database_users):
        self.database_users = database_users

    async def add_users(self, data: AddUsersSchema):
        await self.database_users.insert_many(list([i.dict() for i in data.users]))
