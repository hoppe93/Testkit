
from datetime import datetime
from sqlalchemy import func, Column, DateTime, Float, Integer, String, and_, or_
from . base import Base
from . import helper

from sqlalchemy.sql.expression import delete, insert, select, update
from . import config


class TestResult(Base):
    

    __tablename__ = 'testresults'


    STATUS_RUNNING = 1
    STATUS_SUCCESS = 2
    STATUS_FAILURE = 3
    STATUS_CANCELLED = 4


    # ID of test result
    id = Column(Integer, primary_key=True)
    # ID of associated test run
    testrunid = Column(Integer)
    # Name of this test
    name = Column(String)
    # Command used to run the simulation
    command = Column(String)
    # Command used to run the check
    checkcommand = Column(String)
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


    def durationf(self, html=False):
        """
        Return the duration of the test run as a string.
        """
        if self.duration is None:
            if self.starttime is not None:
                d = (datetime.now() - self.starttime).total_seconds()
                return helper.formatDuration(d, html=html)
            else:
                return helper.formatDuration(0, html=html)
        else:
            return helper.formatDuration(self.duration, html=html)


    def finish(self, success, duration, report, error='', endtime=None):
        """
        Finish this test with the given result.
        """
        if endtime is None:
            endtime = datetime.now()

        s = self.STATUS_SUCCESS if success else self.STATUS_FAILURE
        return TestResult.save(
            id=self.id,
            status=s,
            duration=duration,
            report=report,
            error=error,
            endtime=endtime
        )


    @staticmethod
    def cancel(runid):
        """
        Cancel all running tests for the specified test run.
        """
        db = config.database()
        return db.exe(update(TestResult).values(status=TestResult.STATUS_CANCELLED).where(TestResult.testrunid==runid))


    @staticmethod
    def finish_running(runid, success, endtime=None, error=''):
        """
        Finish all test results with status 'RUNNING' of the specified run.
        """
        if endtime is None:
            endtime = datetime.now()

        db = config.database()
        s = TestResult.STATUS_SUCCESS if success else TestResult.STATUS_FAILURE
        return db.exe(update(TestResult).values(
            status=s, endtime=endtime,
            error=error
        ).where(TestResult.testrunid==runid))


    @staticmethod
    def get(id):
        return helper.get(TestResult, id)


    @staticmethod
    def getOfRun(runid):
        """
        Return all test results of the specified TestRun.
        """
        db = config.database()
        return db.exe(select(TestResult).where(TestResult.testrunid==runid).order_by(TestResult.id)).scalars().all()


    @staticmethod
    def getOfRunWithName(runid, name):
        """
        Return all test results with the specified name of the given TestRun.
        """
        db = config.database()
        return db.exe(select(TestResult).where(and_(TestResult.testrunid==runid, TestResult.name==name))).scalars().all()


    @staticmethod
    def search(q, offset=None, limit=100):
        """
        Search for test runs with the given query.
        """
        db = config.database()
        eq = q.replace('%', '%%')

        stmt = select(TestResult).where(or_(
            TestResult.name.like(f'%{eq}%'),
            TestResult.command.like(f'%{eq}%'),
            TestResult.checkcommand.like(f'%{eq}%'),
            TestResult.report.like(f'%{eq}%'),
            TestResult.error.like(f'%{eq}%')
        )).limit(limit)

        if offset:
            stmt = stmt.offset(offset)

        return db.exe(stmt).scalars().all()


    @staticmethod
    def start(name, testrunid, starttime=None, command='', checkcommand=''):
        """
        Start a single test module.
        """
        if starttime is None:
            starttime = datetime.now()

        return TestResult.save(
            name=name, testrunid=testrunid, starttime=starttime,
            status=TestResult.STATUS_RUNNING, command=command,
            checkcommand=checkcommand
        )


    @staticmethod
    def save(id=None, **kwargs):
        return helper.save(TestResult, id=id, **kwargs)


