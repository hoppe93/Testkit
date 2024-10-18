
from .Task import Task


class TestCase:
    

    def __init__(self, name, exec, result):
        """
        Constructor.
        """
        self.name = name
        self.exec = exec
        self.result = result


    def task(self, testrun, nthreads=None, timeout=None):
        """
        Run the test case.
        """
        return Task(self.exec, testrun=testrun, nthreads=nthreads, timeout=timeout)


    def getResult(self):
        """
        Return the result of the test.
        """
        pass


