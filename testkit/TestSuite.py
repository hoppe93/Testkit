# Class representing a test suite

import json
from pathlib import Path
import traceback

from Code import Code
from TestCase import TestCase

import db


class TestSuite:
    

    def __init__(self, config, branch=None, commit=None):
        """
        Constructor.
        """
        if type(config) == str or type(config) == Path:
            self.loadConfigFile(config, branch=branch, commit=commit)
        else:
            # Assume json
            self.loadConfig(config, branch=branch, commit=commit)


    def getPreviousRuns(self):
        """
        Returns all previous runs for this test suite and for the current
        code version.
        """
        commit = self.code.getCommit()
        return TestRun.getByCommit(commit)


    def loadConfigFile(self, config, branch=None, commit=None):
        """
        Load a test suite configuration from the file with the given name.
        """
        self.configPath = config

        with open(config, 'r') as f:
            c = json.load(f)

        self.loadConfig(c)


    def loadConfig(self, config, branch=None, commit=None):
        """
        Load a test suite configuration from the given dict.
        """
        self.config = config

        self.name = config['name']
        self.path = config['path']

        if branch:
            config['code']['branch'] = branch
        if commit:
            config['code']['commit'] = commit

        self.code = Code(**config['code'])
        self.code.build()

        self.tests = []
        for test in config['tests']:
            self.tests.append(TestCase(**test))


    def run(self, n=4, nthreads=None, timeout=None):
        """
        Run all tests.

        :param n: Number of tasks to run in parallel.
        """
        queue = []
        active = []
        tasks = []

        # Change current working directory
        os.chdir(self.path)

        # Create a database entry
        tr = db.TestRun.start(self.code.getCommit())

        try:
            finished = 0

            for test in self.tests:
                task = test.task(nthreads=nthreads, timeout=timeout)
                queue.append(task)
                tasks.append(task)

            while len(queue) > 0 or len(active) > 0:
                for task in active:
                    if task.isFinished(0.1):
                        active.remove(task)
                        finished += 1

                while len(queue) > 0 and len(active) < n:
                    task = queue.pop(0)
                    task.run()
                    active.append(task)

            # Check results
            success = True
            for task in tasks:
                if task.checkResult() != True:
                    success = False

            if success:
                tr.finish(success)
            else:
                tr.finish(success, error='One or more tests failed.')
        except Exception as ex:
            tr.finish(False, error=traceback.format_exception(e))


