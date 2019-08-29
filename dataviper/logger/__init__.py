
class NaivePrintLogger():
    """
    Not recommended
    """
    def __init__(self):
        pass


    def info(self, msg, *args):
        print("\t", msg, *args)


    def error(self, tag, *args):
        print("\tError [{}]".format(tag), ":", *args)
