# file: mongoConnection.py
import pymongo
from pymongo.errors import ConnectionFailure


class MongoConnection:
    """A class to manage a connection to MongoDB."""

    def __init__(self, db_name, host='localhost', port=27017):
        self.db_name = db_name
        self.host = host
        self.port = port
        self.client = None
        self.db = None  # self.db starts as None
        self._connect()

    def _connect(self):
        """Establishes the connection to the MongoDB database."""
        try:
            self.client = pymongo.MongoClient(self.host, self.port, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ismaster')
            self.db = self.client[self.db_name]  # self.db is assigned a Database object here
            print(f"MongoDB connection successful to database '{self.db_name}'.")
        except ConnectionFailure as e:
            print(f"Could not connect to MongoDB: {e}")
            raise

    def get_collection(self, collection_name):
        """Returns a collection object from the database."""
        # --- THE FIX IS HERE ---
        # Instead of "if self.db:", use "if self.db is not None:"
        if self.db is not None:
            return self.db[collection_name]
        else:
            print("Database not connected. Cannot get collection.")
            return None

    def close(self):
        """Closes the MongoDB connection."""
        if self.client:
            self.client.close()
            print("MongoDB connection closed.")