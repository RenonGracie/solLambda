from functools import wraps

from sqlalchemy import create_engine, URL
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from src.models.db.analytic_event import AnalyticEvent
from src.models.db.clients import ClientSignup
from src.models.db.therapist_videos import TherapistVideoModel
from src.models.db.therapists import AppointmentModel, TherapistModel
from src.utils.settings import settings
from src.utils.singletone import Singleton

import boto3


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
            print(f"An error occurred: {e}")
            raise
        finally:
            session.close()

    return wrapper


def get_db_url() -> (URL, dict):
    rds_host = settings.RDS_HOST
    rds_port = settings.RDS_PORT
    rds_username = settings.RDS_USER
    database = settings.RDS_DATABASE

    if not rds_host:
        raise ValueError("RDS_HOST environment variable is not set")

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
        TherapistModel.__table__.create(self._engine, checkfirst=True)
        AppointmentModel.__table__.create(self._engine, checkfirst=True)
        TherapistVideoModel.__table__.create(self._engine, checkfirst=True)
        AnalyticEvent.__table__.create(self._engine, checkfirst=True)

        session_maker = sessionmaker(bind=self._engine)
        self.session = session_maker()

    def drop_appointments(self):
        AppointmentModel.__table__.drop(self._engine)
        AppointmentModel.__table__.create(self._engine, checkfirst=True)


_database = _Database()
db = _database.session


def drop_appointments():
    _database.drop_appointments()
