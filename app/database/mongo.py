import os

from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine


class MongoDB:
    def __init__(self):
        self.client = None
        self.engine = None

    def connect(self):
        self.client = AsyncIOMotorClient(os.environ.get("MONGO_DB_URL"))
        self.engine = AIOEngine(
            client=self.client, database=os.environ.get("MONGO_DB_NAME")
        )

    def close(self):
        self.client.close()
