from pprint import pprint
from kafka import KafkaConsumer
import json

class Consumer:
    def __init__(self, topic):
        self.consumer = KafkaConsumer(topic,
                                 group_id='my-group',
                                 value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                                 bootstrap_servers=['localhost:9092']
                                 # consumer_timeout_ms=10000
        )

    def print_messages(self):
        for messages in self.consumer:
            pprint(messages.value)




consumer = Consumer('interesting_data')
consumer.print_messages()