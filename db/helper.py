
from sqlalchemy.sql.expression import delete, insert, select, update
from . import config


def get(cls, id):
    """
    Get the item of the specified type with the specified ID.
    """
    db = config.database()
    return db.exe(select(cls).where(cls.id == id)).scalars().one_or_none()


def save(cls, id=None, **kwargs):
    """
    Save the given student to the database. If an ID is given,
    the student record is updated rather than inserted.
    """
    db = config.database()

    if id  is not None:
        stmt = update(cls).where(cls.id==id)
    else:
        stmt = insert(cls)

    stmt = stmt.values(**kwargs)
    result = db.exe(stmt, commit=True)

    if id is None:
        return get(cls, result.inserted_primary_key[0])
    else:
        return get(cls, id)


