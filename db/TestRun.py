
from datetime import datetime
from sqlalchemy import func, Column, DateTime, Integer, String
from . base import Base
from . import helper

from sqlalchemy.sql.expression import delete, insert, select, update
from . import config


class TestRun(Base):
    

    __tablename__ = 'testruns'


    STATUS_RUNNING = 1
    STATUS_SUCCESS = 2
    STATUS_FAILURE = 3


    # Test-run ID
    id = Column(Integer, primary_key=True)
    # Name of test suite
    suitename = Column(String)
    # Start time of test
    starttime = Column(DateTime)
    # End time of test
    endtime = Column(DateTime)
    # Git commit for code
    commit = Column(String)
    # Status
    status = Column(Integer)
    # Error message
    error = Column(String)


    def finish(self, success, endtime=None, error=''):
        """
        Finish this test run.
        """
        if endtime is None:
            endtime = datetime.now()

        s = self.STATUS_SUCCESS if success else self.STATUS_FAILURE
        return TestRun.save(id=self.id, endtime=endtime, status=s, error=error)


    @staticmethod
    def get(id):
        return helper.get(TestRun, id=id)


    @staticmethod
    def getByCommit(commit):
        """
        Return all runs for the specified commit.
        """
        db = config.database()
        return db.exe(select(TestRun).where(TestRun.commit==commit)).scalars().all()


    @staticmethod
    def start(suitename, commit, starttime=None):
        """
        Start a test run.
        """
        if starttime is None:
            starttime = datetime.now()

        return TestRun.save(suitename=suitename, commit=commit, starttime=starttime, status=TestRun.STATUS_RUNNING)


    @staticmethod
    def save(id=None, **kwargs):
        return helper.save(TestRun, id=id, **kwargs)


