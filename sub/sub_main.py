from mongoConnection import MongoConnection
from sub.parser import DataParser
from sub.writer import MongoWriter
from sub.consumer import Consumer

if __name__ == "__main__":
    KAFKA_TOPIC = 'interesting_data'
    MONGO_DB_NAME = 'newsgroups_db'
    MONGO_COLLECTION_NAME = 'interesting_posts' # <--- Specific collection

    mongo_connection = None
    try:
        mongo_connection = MongoConnection(db_name=MONGO_DB_NAME)
        data_parser = DataParser()
        mongo_writer = MongoWriter(mongo_connection, collection_name=MONGO_COLLECTION_NAME)
        consumer = Consumer(topic=KAFKA_TOPIC, parser=data_parser, writer=mongo_writer)
        consumer.start_consuming()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if mongo_connection:
            mongo_connection.close()