import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

"""
Instalieren um mit server vebunden zusein
pip install pymongo.server_api

"""
load_dotenv()


class DataHandler:
    MONGO_URI = os.getenv("MONGO_URI")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "budgetplanner")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "accounts")

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            if not cls.MONGO_URI:
                raise ValueError("MONGO_URI fehlt. Bitte .env Datei prüfen.")

            cls._instance.client = MongoClient(
                cls.MONGO_URI,
                server_api=ServerApi("1")
            )

            cls._instance.db = cls._instance.client[cls.DATABASE_NAME]
            cls._instance.collection = cls._instance.db[cls.COLLECTION_NAME]
            cls._instance.accounts = cls._instance._laden()

        return cls._instance


    def _laden(self):
        """Lädt Accounts aus MongoDB oder gibt leere Struktur zurück."""
        docs = list(self.collection.find({}))

        if not docs:
            return {}

        accounts = {}
        for doc in docs:
            email = doc["email"]
            doc.pop("_id", None)
            accounts[email] = doc

        return accounts

    def speichern(self):
        """Speichert alle Accounts in MongoDB."""
        self.collection.delete_many({})
        for email, account in self.accounts.items():
            self.collection.insert_one(account)
