
from pathlib import Path


DB = None


def database():
    return DB


def init(db):
    global DB
    DB = db


def rootpath():
    """
    Returns the path to the course manager root directory.
    """
    return str(Path(__file__).parent.resolve().absolute())


