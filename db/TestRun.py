
from datetime import datetime
from sqlalchemy import func, Column, DateTime, Integer, String, or_
from . base import Base
from . import helper

from sqlalchemy.sql.expression import delete, insert, select, update
from . import config, TestResult


class TestRun(Base):
    

    __tablename__ = 'testruns'


    STATUS_RUNNING = 1
    STATUS_SUCCESS = 2
    STATUS_FAILURE = 3
    STATUS_CANCELLED = 4


    # Test-run ID
    id = Column(Integer, primary_key=True)
    # Name of test suite
    suitename = Column(String)
    # Code URL
    codeurl = Column(String)
    # Code branch
    codebranch = Column(String)
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


    def cancel(self, endtime=None, error='The test was cancelled.'):
        """
        Mark this test run as cancelled in the database.
        """
        if endtime is None:
            endtime = datetime.now()

        TestResult.cancel(runid=self.id)

        return TestRun.save(id=self.id, endtime=endtime, status=TestRun.STATUS_CANCELLED, error=error)

        
    def duration(self):
        """
        Return the duration in seconds of this test run.
        """
        if self.starttime is None and self.endtime is None:
            return 0
        elif self.endtime is None:
            return (datetime.now() - self.starttime).total_seconds()

        return (self.endtime - self.starttime).total_seconds()


    def durationf(self, html=False):
        """
        Return the duration of the test run as a string.
        """
        d = self.duration()
        return helper.formatDuration(d, html=html)


    def finish(self, success, endtime=None, error=''):
        """
        Finish this test run.
        """
        if endtime is None:
            endtime = datetime.now()

        s = self.STATUS_SUCCESS if success else self.STATUS_FAILURE
        return TestRun.save(id=self.id, endtime=endtime, status=s, error=error)


    def finish_running(self, success, endtime=None, error=''):
        """
        Finish all test results with status 'RUNNING' of this run.
        """
        return TestResult.finish_running(self.id, success=success, endtime=endtime, error=error)


    def results(self):
        """
        Return all results of this test run.
        """
        return TestResult.getOfRun(self.id)


    def summarize(self):
        """
        Summarize the result of this test run.
        """
        results = TestResult.getOfRun(self.id)
        
        failure = 0
        success = 0
        for r in results:
            if r.status == TestResult.STATUS_SUCCESS:
                success += 1
            else:
                failure += 1


        return success, failure


    @staticmethod
    def count():
        """
        Count the number of test runs in the database.
        """
        db = config.database()
        return db.exe(select(func.count(TestRun.id))).one_or_none()[0]


    @staticmethod
    def get(id):
        return helper.get(TestRun, id=id)


    @staticmethod
    def getall(page=None, per_page=100):
        db = config.database()

        stmt = select(TestRun).order_by(TestRun.starttime.desc()).limit(per_page)
        if page is not None:
            stmt.offset(page*per_page)

        return db.exe(stmt).scalars().all()


    @staticmethod
    def getByCommit(commit):
        """
        Return all runs for the specified commit.
        """
        db = config.database()
        return db.exe(select(TestRun).where(TestRun.commit==commit)).scalars().all()


    @staticmethod
    def search(q, offset=None, limit=100):
        """
        Search for test runs with the given query.
        """
        db = config.database()
        eq = q.replace('%', '%%')

        stmt = select(TestRun).where(or_(
            TestRun.suitename.like(f'%{eq}%'),
            TestRun.codeurl.like(f'%{eq}%'),
            TestRun.codebranch.like(f'%{eq}%'),
            TestRun.commit.like(f'%{eq}%'),
            TestRun.error.like(f'%{eq}%')
        )).limit(limit)

        if offset:
            stmt = stmt.offset(offset)

        return db.exe(stmt).scalars().all()


    @staticmethod
    def start(suitename, commit, starttime=None, codebranch=None, codeurl=None):
        """
        Start a test run.
        """
        if starttime is None:
            starttime = datetime.now()

        opts = {}
        if codebranch:
            opts['codebranch'] = codebranch
        if codeurl:
            opts['codeurl'] = codeurl

        return TestRun.save(
            suitename=suitename, commit=commit, starttime=starttime,
            status=TestRun.STATUS_RUNNING, **opts
        )


    @staticmethod
    def save(id=None, **kwargs):
        return helper.save(TestRun, id=id, **kwargs)


