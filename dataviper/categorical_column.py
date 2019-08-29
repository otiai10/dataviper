
class CategoricalColumn():

    def __init__(self, name, values=[]):
        self.name = name
        self.values = values


    def gen_pivot_column_name(self, val):
        return "{}_{}".format(self.name, val)
