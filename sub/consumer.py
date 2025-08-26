from pprint import pprint

from dns import exception
from kafka import KafkaConsumer
import json


class Consumer:
    def __init__(self, topic, parser, writer):
        """
        Initializes the Kafka Consumer.

        Args:
            topic (str): The Kafka topic to subscribe to.
            parser (DataParser): An instance of the parser class.
            writer (MongoWriter): An instance of the writer class.
        """
        self.topic = topic
        self.parser = parser
        self.writer = writer
        self.consumer = KafkaConsumer(
            self.topic,
            group_id='mongo-writer-group',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            bootstrap_servers=['localhost:9092'],
            auto_offset_reset='earliest'  # Start reading from the beginning of the topic
        )
        print(f"Kafka consumer subscribed to topic '{self.topic}'.")

    def start_consuming(self):
        """Starts the main loop to listen for, parse, and write messages."""
        print("Starting to listen for messages...")
        try:
            for message in self.consumer:
                print("\n--- New Message Received ---")
                pprint(message.value)

                # Step 1: Parse the data
                parsed_documents = self.parser.parse(message.value)
                print(f"Parsed into {len(parsed_documents)} documents.")

                # Step 2: Write the data to MongoDB
                self.writer.write_many(parsed_documents)

        except exception.KafkaError as a:
            print(f"An error occurred during Kafka consumption: {a}")
        finally:
            # Clean up resources
            self.consumer.close()
            print("Kafka consumer closed.")

