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
        self.newsgroups_interesting = fetch_20newsgroups(subset='all', categories=self.interesting_categories)
        self.newsgroups_not_interesting = fetch_20newsgroups(subset='all', categories=self.not_interesting_categories)

    def batch_generator(self,data, batch_size=None):
        if batch_size is None:
            batch_size = self.batch_size
        for i in range(0, len(data), batch_size):
            yield data[i:i + batch_size]

    def get_interesting_data(self):
        data = next(self.batch_generator(self.newsgroups_interesting.data))
        return data
    def get_not_interesting_data(self):
        data = next(self.batch_generator(self.newsgroups_not_interesting.data))
        return data



