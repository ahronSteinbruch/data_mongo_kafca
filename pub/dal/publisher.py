from dal.fetcher import DataFetcher
from pub.producer import Producer
from datetime import datetime
import time
class Publisher:
    def __init__(self):
        self.fetcher = DataFetcher()
        self.producer = Producer()
    def publish(self):
        data = self.get_data()
        for key in data.keys():
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.producer.publish_message(key,{timestamp:data[key]})
            time.sleep(1)

    def get_data(self):
        interesting_data = self.fetcher.get_interesting_data()
        not_interesting_data = self.fetcher.get_not_interesting_data()
        return {'interesting_data': interesting_data, 'not_interesting_data': not_interesting_data}
