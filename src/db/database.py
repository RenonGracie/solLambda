from functools import wraps

import boto3
from sqlalchemy import URL, create_engine, text
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


def get_db_url() -> tuple[URL, dict]:
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
        try:
            client = boto3.client("dsql", region_name=region)
            password = client.generate_db_connect_admin_auth_token(
                Hostname=rds_host,
                Region=region,
            )
            args = {"sslmode": "require"}
            logger.info(f"Using IAM authentication for Aurora DSQL at {rds_host}")
        except Exception as e:
            logger.error(f"Failed to generate Aurora DSQL auth token: {e}")
            # Fallback to regular password authentication
            password = settings.RDS_PASSWORD
            args = {"sslmode": "prefer"}
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
        
        # Add connection pool settings for better stability
        self._engine = create_engine(
            url, 
            connect_args=args, 
            isolation_level="AUTOCOMMIT",
            pool_pre_ping=True,  # Verify connections before use
            pool_recycle=3600,   # Recycle connections every hour
            pool_size=5,         # Connection pool size
            max_overflow=10      # Maximum overflow connections
        )

        # Create tables if they don't exist
        try:
            ClientSignup.__table__.create(self._engine, checkfirst=True)
            AirtableTherapist.__table__.create(self._engine, checkfirst=True)
            UnsubscribedEmail.__table__.create(self._engine, checkfirst=True)
            CalendarEvent.__table__.create(self._engine, checkfirst=True)
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise

        session_maker = sessionmaker(bind=self._engine)
        self.session = session_maker()
    
    def execute(self, query, params=None):
        """Execute raw SQL queries"""
        return self.session.execute(text(query), params or {})
    
    def commit(self):
        """Commit the current transaction"""
        self.session.commit()
    
    def rollback(self):
        """Rollback the current transaction"""
        self.session.rollback()


_database = _Database()
db = _database.session

# Add convenience methods to the session
db.execute = _database.execute
db.commit = _database.commit
db.rollback = _database.rollback