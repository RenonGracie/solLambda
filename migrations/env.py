# migrations/env.py
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

# Import your models here for autogenerate support
# This is crucial so Alembic can compare your models to the database schema.
from src.models.db.base import Base # Assuming all your models inherit from this Base
from src.models.db.signup_form import ClientSignup # Import specific models if needed for autogenerate
from src.models.db.airtable import AirtableTherapist # Import other models you want Alembic to track
# Add other model imports as necessary, e.g., from src.models.db.<your_model_file> import YourModel

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata # Ensure this points to the Base from which all your models inherit

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def get_db_url_and_args_for_alembic():
    """
    Constructs the database URL and connection args for Alembic.
    Handles IAM authentication for AWS environments.
    """
    is_aws = os.getenv("IS_AWS", "false").lower() == "true"
    env_name = os.getenv("ENV", "local")

    db_host = os.getenv("RDS_HOST")
    db_port = os.getenv("RDS_PORT", "5432")
    db_database = os.getenv("RDS_DATABASE")
    db_user = os.getenv("RDS_USER")

    if is_aws or env_name != "local":
        # For AWS environments, use IAM authentication
        if db_host and db_database and db_user:
            try:
                import boto3
                
                # Generate IAM auth token
                region = "us-east-2"
                client = boto3.client("dsql", region_name=region)
                password = client.generate_db_connect_admin_auth_token(
                    Hostname=db_host,
                    Region=region,
                )
                
                url = f"postgresql://{db_user}:{password}@{db_host}:{db_port}/{db_database}"
                args = {"sslmode": "require"}
                
                print(f"INFO: Using IAM authentication for Aurora DSQL at {db_host}")
                return url, args
                
            except Exception as e:
                print(f"ERROR: Failed to generate IAM token: {e}")
                # Fallback to password if provided
                db_password = os.getenv("RDS_PASSWORD", "")
                url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_database}"
                args = {"sslmode": "require"}
                return url, args
        else:
            print("WARNING: Insufficient RDS environment variables for Alembic. Falling back to SQLite.")
            return "sqlite:///./sql_app.db", {}

    else: # Local development
        db_password = os.getenv("RDS_PASSWORD", "")

        if db_host and db_database and db_user:
            # Local PostgreSQL connection
            print("INFO: Connecting to local PostgreSQL for Alembic.")
            url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_database}"
            args = {"sslmode": "prefer"}
            return url, args
        else:
            # Default to SQLite for basic local testing if no PostgreSQL is configured
            print("INFO: No local PostgreSQL configured. Using SQLite for Alembic.")
            return "sqlite:///./sql_app.db", {}


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url, args = get_db_url_and_args_for_alembic()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    url, args = get_db_url_and_args_for_alembic()
    
    connectable = create_engine(
        url,
        connect_args=args,  # This includes sslmode settings
        poolclass=pool.NullPool, # NullPool is often good for short-lived scripts like migrations
        isolation_level="AUTOCOMMIT"  # Match your main app's setting
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()