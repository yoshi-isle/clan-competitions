from logging import Logger
import os
from dotenv import load_dotenv
from pymongo import MongoClient

class Database:
    def __init__(self, logger: Logger):
        load_dotenv()
        
        self.logger = logger
        self.client=MongoClient(os.getenv("MONGO_CONNECTION_STRING"))
        self.db=self.client["competitionsDB"]
        self.competition_collection=self.db["competitions"]
        if not self.client:
            self.logger.critical("Database not connected")
