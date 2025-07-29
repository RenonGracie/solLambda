from functools import wraps

import boto3
from sqlalchemy import URL, create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from src.models.db.airtable import AirtableTherapist
from src.models.db.calendar_events import CalendarEvent
from src.models.db.signup_form import ClientSignup
from src.models.db.unsubscribed_emails import UnsubscribedEmail
from src.utils.logger import get_logger
from src.utils.settings import settings
from src.utils.singletone import Singleton

logger = get_logger()


def with_database(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        session = db
        try:
            result = func(session, *args, **kwargs)
            session.commit()
            return result
        except SQLAlchemyError as e:
            session.rollback()
            logger.error("Database error", extra={"error": str(e)})
            raise
        finally:
            session.close()

    return wrapper


def get_db_url() -> (URL, dict):
    rds_host = settings.RDS_HOST
    rds_port = settings.RDS_PORT
    rds_username = settings.RDS_USER
    database = settings.RDS_DATABASE

    # Fallback to an in-memory SQLite database when RDS settings are not provided (e.g., during unit tests)
    if not rds_host:
        logger.warning(
            "RDS_HOST is not set – falling back to an in-memory SQLite database."
        )
        return URL.create("sqlite+pysqlite", database=":memory:"), {}

    if settings.IS_AWS is True:
        region = "us-east-2"
        client = boto3.client("dsql", region_name=region)
        password = client.generate_db_connect_admin_auth_token(
            Hostname=rds_host,
            Region=region,
        )
        args = {"sslmode": "require"}
    else:
        password = settings.RDS_PASSWORD
        args = {"sslmode": "prefer"}

    return URL.create(
        "postgresql",
        username=rds_username,
        password=password,
        host=rds_host,
        database=database,
        port=rds_port,
    ), args


class _Database(Singleton):
    def __init__(self):
        url, args = get_db_url()
        self._engine = create_engine(
            url, connect_args=args, isolation_level="AUTOCOMMIT"
        )

        ClientSignup.__table__.create(self._engine, checkfirst=True)
        AirtableTherapist.__table__.create(self._engine, checkfirst=True)
        UnsubscribedEmail.__table__.create(self._engine, checkfirst=True)
        CalendarEvent.__table__.create(self._engine, checkfirst=True)

        session_maker = sessionmaker(bind=self._engine)
        self.session = session_maker()


_database = _Database()
db = _database.session
