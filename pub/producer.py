from kafka import KafkaProducer
import json


class Producer:
    def _init_(self, bootstrap_servers='localhost:9092',
               encode='utf-8'):
        self.producer = KafkaProducer(bootstrap_servers=[bootstrap_servers],
                                      value_serializer=lambda x:
                                      json.dumps(x).encode(encode))

    def publish_message(self, topic, message):
        self.producer.send(topic,message)
