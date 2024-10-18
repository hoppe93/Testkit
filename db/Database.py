# Database manager

from pathlib import Path
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from datetime import datetime
from . base import Base


class Database:
    

    def __init__(self, filename, echo=False):
        """
        Constructor.
        """
        initdb = not Path(filename).is_file()

        self.engine = create_engine(f'sqlite:///{filename}', echo=echo)

        if initdb:
            Base.metadata.create_all(self.engine)

        self.session = Session(self.engine)


    def exe(self, stmt, commit=False):
        r = self.session.execute(stmt)

        if commit:
            self.session.commit()

        return r


    def flush(self):
        self.session.flush()
        self.session.commit()


    def now(self, time=True):
        """
        Return the current date (and time) as a string.
        """
        now = datetime.now()

        if time:
            return now.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return now.strftime('%Y-%m-%d')


    def query(self, stmt):
        return self.session.query(stmt)


