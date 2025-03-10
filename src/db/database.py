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
    password = settings.RDS_PASSWORD

    if settings.IS_AWS is True:
        region = "us-east-2"
        client = boto3.client("rds", region_name=region)
        db_instance = client.describe_db_instances(
            DBInstanceIdentifier=settings.DB_INSTANCE_IDENTIFIER
        )['DBInstances'][0]
        print(db_instance)
        print(db_instance['Endpoint'])
        rds_host = db_instance['Endpoint']['Address']
        rds_port = db_instance['Endpoint']['Port']

        args = {"sslmode": "require"}
    else:
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
        engine = create_engine(url, connect_args=args, isolation_level="AUTOCOMMIT")

        ClientSignup.__table__.create(engine, checkfirst=True)
        TherapistModel.__table__.create(engine, checkfirst=True)
        AppointmentModel.__table__.create(engine, checkfirst=True)
        TherapistVideoModel.__table__.create(engine, checkfirst=True)
        AnalyticEvent.__table__.create(engine, checkfirst=True)

        session_maker = sessionmaker(bind=engine)
        self.session = session_maker()


db = _Database().session
