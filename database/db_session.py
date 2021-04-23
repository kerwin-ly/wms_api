from database.mysql_db import db


def session_commit() -> None:
    try:
        db.session.commit()
    except Exception as err:
        db.session.rollback()
        raise err


def session_flush(*instances: db.Model) -> None:
    try:
        db.session.flush(instances)
    except Exception as err:
        db.session.rollback()
        raise err


class DatabaseOperateMixin(object):
    def flush(self) -> object:
        db.session.add(self)
        session_flush(self)
        return self

    def commit(self) -> object:
        db.session.add(self)
        session_commit()
        return self
