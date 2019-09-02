from abc import ABC, abstractclassmethod

class DataSource(ABC):

    @abstractclassmethod
    def get_schema(self, table_name):
        pass


    @abstractclassmethod
    def count_total(self, profile):
        pass


    @abstractclassmethod
    def count_null(self, profile):
        pass


    @abstractclassmethod
    def get_deviation(self, profile):
        pass


    @abstractclassmethod
    def get_variation(self, profile):
        pass


    @abstractclassmethod
    def get_examples(self, profile):
        pass


    @abstractclassmethod
    def onehot_encode(self, profile, key, categorical_columns, result_table, commit=False):
        pass


    @abstractclassmethod
    def joinability(self, on):
        pass
