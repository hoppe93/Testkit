

class BuildException(Exception):
    

    def __init__(self, msg, out, err):
        """
        Constructor.

        :param msg: Error message.
        :param out: Result on stdout from the build process.
        :param err: Result on stderr from the build process.
        """
        super().__init__(msg)

        self.out = out
        self.err = err


