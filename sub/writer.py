class MongoWriter:
    """Writes data to a specific MongoDB collection."""

    def __init__(self, mongo_connection, collection_name):
        self.collection = mongo_connection.get_collection(collection_name)
        if not self.collection:
            raise ValueError("Could not get MongoDB collection. Check connection.")
        print(f"MongoWriter initialized for collection '{collection_name}'.")

    def write_many(self, documents):
        """Writes a list of documents to the collection."""
        if not documents:
            print("No documents to write.")
            return

        try:
            result = self.collection.insert_many(documents)
            print(f"Successfully inserted {len(result.inserted_ids)} documents.")
        except Exception as e:
            print(f"An error occurred during MongoDB insertion: {e}")