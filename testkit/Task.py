# Task

import os
import time
import subprocess


class Task:
    

    ERROR_TIMEOUT = 1
    ERROR_KEYBOARDINTERRUPT = 2
    ERROR_CODE = 3
    

    def __init__(self, command, checkcmd, testrun, nthreads=None, timeout=None):
        """
        Constructor.
        """
        self.command = command
        self.checkcmd = checkcmd
        self.testrun = testrun
        self.nthreads = nthreads
        self.timeout = timeout

        self.process = None
        self.starttime = None
        self.endtime = None
        self.errorOnExit = None


    def checkResult(self):
        """
        Check the result of the simulation.
        """
        # Test is not finished
        if self.endtime is None:
            return None

        if self.errorOnExit is not None:
            return False

        # Execute the check command
        try:
            cmd = self.checkcmd.split(' ')
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()

            self.testresult.finish(
                # Success/failure?
                (self.returncode==0),
                # Duration
                self.endtime-self.starttime,
                # Report from check program
                report=out.decode('utf-8'),
                # Error message(s)
                error=err.decode('utf-8')
            )

            return (self.returncode==0)
        except Exception as ex:
            self.testresult.finish(
                False,
                self.endtime-self.starttime,
                report='Error while checking test result.',
                error=traceback.format_exception(ex)
            )

            return False


    def run(self):
        """
        Run this task.
        """
        self.starttime = time.time()
        self.testresult = db.TestResult.start(self.testrun.id)

        if self.process is not None:
            return

        env = None
        if self.nthreads is not None:
            env = os.environ.copy()
            env['OMP_NUM_THREADS'] = str(self.nthreads)

        cmd = self.command.split(' ')
        self.process = subprocess.Popen(cmd, env=env)


    def isFinished(self, timeout=1):
        """
        Check if this task is finished or not.
        """
        try:
            b = self.process.communicate(timeout=timeout)[1]
            if b is not None:
                self.stderr_data = b.decode('utf-8')

            self.endtime = time.time()

            if self.process.returncode != 0:
                self.errorOnExit = ERROR_CODE

                self.testresult.finish(
                    False, self.endtime-self.starttime,
                    report=f'Code exited with a non-zero exit code ({self.process.returncode}).',
                    error=self.stderr_data
                )
            else:
                self.errorOnExit = None

        except subprocess.TimeoutExpired:
            if self.timeout and (time.time() - self.starttime > self.timeout):
                self.process.kill()
                self.errorOnExit = ERROR_TIMEOUT
                self.endtime = time.time()
                self.testresult.finish(
                    False, self.endtime-self.starttime,
                    report='Killed by timeout.',
                    error='Killed by timeout.'
                )
                return True
            return False
        except KeyboardInterrupt:
            self.errorOnExit = ERROR_KEYBOARDINTERRUPT
            self.endtime = time.time()

            self.testresult.finish(
                False, self.endtime-self.starttime,
                report='Killed by user.',
                error='Killed by user.'
            )

        return True


