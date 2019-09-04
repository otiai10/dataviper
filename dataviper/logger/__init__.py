import sys

class IndentLogger():
    """
    Not recommended
    """
    def __init__(self, writer=sys.stdout):
        self.writer = writer
        self.depth = 0


    def __write(self, msg, *args):
        if len(args):
            self.writer.write(" ".join(list(map(lambda v: str(v), [msg] + list(args)))))
        else:
            self.writer.write(msg)


    def enter(self, msg, *args):
        self.__write("\t" * self.depth)
        self.__write(msg, *args)
        self.__write("\n")
        self.depth += 1


    def exit(self, msg, *args):
        self.depth -= 1
        if self.depth < 0:
            self.depth = 0
        self.__write("\t" * self.depth)
        self.__write(msg, *args)
        self.__write("\n")


    def info(self, msg, *args):
        self.__write("\t" * self.depth)
        self.__write(msg, *args)
        self.__write("\n")


    def error(self, tag, *args):
        self.__write("\t" * (self.depth + 1))
        self.__write("ERROR [{}]".format(tag), *args)
        self.__write("\n")
