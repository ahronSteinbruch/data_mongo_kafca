from sklearn.datasets import fetch_20newsgroups

class DataFetcher():
    def __init__(self):
        self.batch_size = 10
        self.interesting_categories = [
            'alt.atheism',
            'comp.graphics',
            'comp.os.ms-windows.misc',
            'comp.sys.ibm.pc.hardware',
            'comp.sys.mac.hardware',
            'comp.windows.x',
            'misc.forsale',
            'rec.autos',
            'rec.motorcycles',
            'rec.sport.baseball',
        ]
        self.not_interesting_categories = [
            'rec.sport.hockey',
            'sci.crypt',
            'sci.electronics',
            'sci.med',
            'sci.space',
            'soc.religion.christian',
            'talk.politics.guns',
            'talk.politics.mideast',
            'talk.politics.misc',
            'talk.religion.misc',
        ]
        # Set return_X_y to True to get both data and target labels
        self.newsgroups_interesting_data, self.newsgroups_interesting_targets = fetch_20newsgroups(
            subset='all', categories=self.interesting_categories, return_X_y=True)
        self.newsgroups_not_interesting_data, self.newsgroups_not_interesting_targets = fetch_20newsgroups(
            subset='all', categories=self.not_interesting_categories, return_X_y=True)

        # Store the category names for mapping
        self.interesting_category_names = fetch_20newsgroups(subset='all',
                                                             categories=self.interesting_categories).target_names
        self.not_interesting_category_names = fetch_20newsgroups(subset='all',
                                                                 categories=self.not_interesting_categories).target_names

    def batch_generator(self, data, targets, batch_size=None):
        if batch_size is None:
            batch_size = self.batch_size
        for i in range(0, len(data), batch_size):
            yield data[i:i + batch_size], targets[i:i + batch_size]

    def get_interesting_data(self):
        data_batch, target_batch = next(
            self.batch_generator(self.newsgroups_interesting_data, self.newsgroups_interesting_targets))
        return self._format_data(data_batch, target_batch, self.interesting_category_names)

    def get_not_interesting_data(self):
        data_batch, target_batch = next(
            self.batch_generator(self.newsgroups_not_interesting_data, self.newsgroups_not_interesting_targets))
        return self._format_data(data_batch, target_batch, self.not_interesting_category_names)

    def _format_data(self, data, targets, category_names):
        """
        Formats the data into a dictionary with category names as keys and data as values
        """
        formatted_data = {}
        for i, text in enumerate(data):
            category_name = category_names[targets[i]]
            if category_name not in formatted_data:
                formatted_data [category_name] = []
            formatted_data[category_name].append(text)
        return formatted_data



