
from sqlalchemy.sql.expression import delete, insert, select, update
from . import config


def formatDuration(duration, html=False):
    """
    Format the given duration (in seconds) as a string.
    """
    DAY = 24*3600
    HOUR = 3600
    MINUTE = 60

    d = 'd'
    h = 'h'
    m = 'm'
    s = 's'
    if html:
        d = '<span class="day">'+d+'</span>'
        h = '<span class="hour">'+h+'</span>'
        m = '<span class="minute">'+m+'</span>'
        s = '<span class="second">'+s+'</span>'

    f = ''
    if duration > DAY:
        days = int(duration/DAY)
        duration -= days*DAY
        f += f'{days:02d}{d}'

    if f or duration > HOUR:
        hours = int(duration/HOUR)
        duration -= hours*HOUR
        f += f'{hours:02d}{h}'

    if f or duration > MINUTE:
        mins = int(duration/MINUTE)
        duration -= mins*MINUTE
        f += f'{mins:02d}{m}'

    if f:
        f += f'{int(duration):02d}{s}'
    else:
        f += f'{duration:.3f}{s}'

    if html:
        return '<span class="time-format">'+f+'</span>'
    else:
        return f


def get(cls, id):
    """
    Get the item of the specified type with the specified ID.
    """
    db = config.database()
    return db.exe(select(cls).where(cls.id == id)).scalars().one_or_none()


def getall(cls):
    """
    Get all items of the specified type.
    """
    db = config.database()
    return db.exe(select(cls)).scalars().all()


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


