# Class representing a test suite

import json
from pathlib import Path
import traceback
import os
import time

from .Code import Code
from .TestCase import TestCase
from . import testlog

import db


class TestSuite:
    

    def __init__(self, config, branch=None, commit=None, skipbuild=False):
        """
        Constructor.
        """
        if type(config) == str or type(config) == Path:
            self.loadConfigFile(config, branch=branch, commit=commit, skipbuild=skipbuild)
        else:
            # Assume json
            self.loadConfig(config, branch=branch, commit=commit, skipbuild=skipbuild)


    def getPreviousRuns(self):
        """
        Returns all previous runs for this test suite and for the current
        code version.
        """
        commit = self.code.getCommit()
        return db.TestRun.getByCommit(commit)


    def loadConfigFile(self, config, branch=None, commit=None, skipbuild=False):
        """
        Load a test suite configuration from the file with the given name.
        """
        self.configPath = config

        with open(config, 'r') as f:
            c = json.load(f)

        self.loadConfig(c, branch=branch, commit=commit, skipbuild=skipbuild)


    def loadConfig(self, config, branch=None, commit=None, skipbuild=False):
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

        if 'nthreads' in config:
            self.nthreads = config['nthreads']
        else:
            self.nthreads = 1

        if 'nprocesses' in config:
            self.nprocesses = config['nprocesses']
        else:
            self.nprocesses = 4

        if 'timeout' in config:
            self.timeout = config['timeout']
        else:
            self.timeout = None

        self.code = Code(**config['code'])

        if skipbuild:
            testlog.info('Skipping code rebuild.')
        else:
            testlog.info('Building code...')
            start = time.time()
            self.code.build()
            testlog.info(f'Finished building code in {time.time()-start:.3f} seconds.')

        self.tests = []
        for test in config['tests']:
            self.tests.append(TestCase(**test))


    def run(self):
        """
        Run all tests.
        """
        queue = []
        active = []
        tasks = []

        # Change current working directory
        testlog.info(f"Changing working directory to '{self.path}'.")
        os.chdir(self.path)

        # Create a database entry
        testlog.info("Starting the test run.")
        tr = db.TestRun.start(self.name, self.code.getCommit())

        try:
            finished = 0

            for test in self.tests:
                task = test.task(testrun=tr, workdir=self.path, nthreads=self.nthreads, timeout=self.timeout)
                queue.append(task)
                tasks.append(task)

            while len(queue) > 0 or len(active) > 0:
                for task in active:
                    if task.isFinished(0.1):
                        active.remove(task)
                        finished += 1

                while len(queue) > 0 and len(active) < self.nprocesses:
                    task = queue.pop(0)
                    testlog.info(f'Launching task {len(tasks)-len(queue)} of {len(tasks)}.')
                    task.run()
                    active.append(task)

            # Check results
            testlog.info('Checking simulation results.')
            success = True
            for task in tasks:
                if task.checkResult() != True:
                    if testlog.use_colors:
                        testlog.info(f"Result of simulation '{task.name}' is \x1B[1;31mFAILURE\x1B[0m.")
                    else:
                        testlog.info(f"Result of simulation '{task.name}' is FAILURE.")

                    success = False
                else:
                    if testlog.use_colors:
                        testlog.info(f"Result of simulation '{task.name}' is \x1B[1;32mSUCCESS\x1B[0m.")
                    else:
                        testlog.info(f"Result of simulation '{task.name}' is SUCCESS.")

            if success:
                tr.finish(success)
            else:
                tr.finish(success, error='One or more tests failed.')
        except KeyboardInterrupt:
            pass
        except Exception as ex:
            testlog.error(f"An error occured while running tests.\n{''.join(traceback.format_exception(ex))}")
            tr.finish(False, error=''.join(traceback.format_exception(ex)))


