from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker

from src.utils.settings import settings
from src.utils.singletone import Singleton
from src.models.db.base import Base

import boto3


class _Database(Singleton):
    def __init__(self):
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

        url = URL.create(
            "postgresql",
            username=rds_username,
            password=password,
            host=rds_host,
            database=database,
            port=rds_port,
        )

        engine = create_engine(url, connect_args=args)

        Base.metadata.create_all(engine)

        session_maker = sessionmaker(bind=engine)
        self.session = session_maker()


db = _Database().session
