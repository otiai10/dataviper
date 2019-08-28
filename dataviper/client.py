
class Client():
    """
    Client is just a proxy for data source.
    """

    def __init__(self, source=None):
        self.source = source


    def connect(self, config=None):
        return self.source.connect(config)


    def get_schema(self, table_name):
        return self.source.get_schema(table_name)


    def count_null(self, profile):
        return self.source.count_null(profile)


    def get_variation(self, profile):
        return self.source.get_variation(profile)


    def get_deviation(self, profile):
        return self.source.get_deviation(profile)


    def get_examples(self, profile):
        return self.source.get_examples(profile)


    def profile(self, table_name):
        profile = self.get_schema(table_name)
        self.count_null(profile)
        self.get_variation(profile)
        self.get_deviation(profile)
        self.get_examples(profile)
        return profile
