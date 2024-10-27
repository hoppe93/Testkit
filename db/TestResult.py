
from datetime import datetime
from sqlalchemy import func, Column, DateTime, Float, Integer, String
from . base import Base
from . import helper

from sqlalchemy.sql.expression import delete, insert, select, update
from . import config


class TestResult(Base):
    

    __tablename__ = 'testresults'


    STATUS_RUNNING = 1
    STATUS_SUCCESS = 2
    STATUS_FAILURE = 3


    # ID of test result
    id = Column(Integer, primary_key=True)
    # ID of associated test run
    testrunid = Column(Integer)
    # Start time of test
    starttime = Column(DateTime)
    # End time of test
    endtime = Column(DateTime)
    # Duration in s
    duration = Column(Float)
    # Status of test
    status = Column(Integer)
    # Report message from the test
    report = Column(String)
    # Error message from the test
    error = Column(String)


    def finish(self, success, duration, report, error='', endtime=None):
        """
        Finish this test with the given result.
        """
        if endtime is None:
            endtime = datetime.now()

        s = self.STATUS_SUCCESS if success else self.STATUS_FAILURE
        return TestResult.save(
            id=self.id,
            report=report,
            error=error,
            endtime=endtime
        )


    @staticmethod
    def get(id):
        return helper.get(TestResult, id)


    @staticmethod
    def getOfRun(runid):
        """
        Return all test results of the specified TestRun.
        """
        db = config.database()
        return db.exe(select(TestResult).where(TestResult.testrunid==runid)).scalars().all()


    @staticmethod
    def start(testrunid, starttime=None):
        """
        Start a single test module.
        """
        if starttime is None:
            starttime = datetime.now()

        return TestResult.save(
            testrunid=testrunid, starttime=starttime,
            status=TestResult.STATUS_RUNNING
        )


    @staticmethod
    def save(id=None, **kwargs):
        return helper.save(TestResult, id=id, **kwargs)


