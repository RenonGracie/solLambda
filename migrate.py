from alembic.config import Config
from alembic import command

from src.db.database import get_db_url


def handler(event, context):
    run_migration()
    return {"statusCode": 200, "body": "Migration completed"}


def run_migration():
    url, args = get_db_url()

    alembic_cfg = Config("/var/task/alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", str(url))

    command.upgrade(alembic_cfg, "head")
