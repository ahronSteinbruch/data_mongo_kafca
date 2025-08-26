class DataParser:
    """Parses incoming data into the desired database format."""

    def parse(self, kafka_message_value):
        """
        Parses a nested dictionary from Kafka into a list of flat documents.
        Each document contains 'text', 'category', and 'timestamp'.
        """
        documents = []
        # e.g., { 1678886400: { 'comp.graphics': ['msg1', 'msg2'] } }
        for timestamp, categories_dict in kafka_message_value.items():
            for category, messages in categories_dict.items():
                for message_text in messages:
                    document = {
                        'text': message_text,
                        'category': category,
                        'timestamp': int(timestamp)  # Ensure timestamp is an integer
                    }
                    documents.append(document)
        return documents