import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool
from dotenv import load_dotenv

# Import your models here to ensure Alembic can see them
from src.models.db.base import Base
from src.models.db.signup_form import ClientSignup
from src.models.db.airtable import AirtableTherapist
# Add other model imports here if you have them

# This is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the target metadata for autogenerate support
target_metadata = Base.metadata

def get_db_url_and_args_for_alembic():
    """
    Constructs the database URL and connection args for Alembic.
    - Uses IAM authentication for 'stg' and 'prod' environments.
    - Uses password authentication for 'dev' environment.
    - Falls back to local SQLite if no other config is found.
    """
    load_dotenv()
    
    env_name = os.getenv("ENV", "local")
    
    db_host = os.getenv("RDS_HOST")
    db_port = os.getenv("RDS_PORT", "5432")
    db_database = os.getenv("RDS_DATABASE")
    db_user = os.getenv("RDS_USER")

    # --- IAM Authentication for Staging and Production ---
    if env_name in ["stg", "prod"]:
        if not all([db_host, db_database, db_user]):
            raise ValueError(f"Required RDS environment variables are missing for '{env_name}'.")

        print(f"INFO: Using IAM authentication for the '{env_name}' environment at host '{db_host}'.")
        try:
            import boto3
            region = "us-east-2"
            client = boto3.client("dsql", region_name=region)
            password = client.generate_db_connect_admin_auth_token(
                Hostname=db_host,
                Region=region,
            )
            
            url = f"postgresql://{db_user}:{password}@{db_host}:{db_port}/{db_database}"
            # SSL is required for IAM connections
            args = {"sslmode": "require"}
            return url, args
            
        except Exception as e:
            print(f"ERROR: Failed to generate IAM token for RDS: {e}")
            raise

    # --- Local Development with Password ---
    db_password = os.getenv("RDS_PASSWORD")
    if db_host and db_user and db_password:
        print(f"INFO: Connecting to local PostgreSQL with password (ENV: {env_name}).")
        url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_database}"
        # SSL is not required for local connections
        args = {"sslmode": "prefer"}
        return url, args

    # --- Fallback to SQLite ---
    print("WARNING: No PostgreSQL configuration found. Falling back to SQLite.")
    return "sqlite:///./sql_app.db", {}

def run_migrations_offline() -> None:
    url, _ = get_db_url_and_args_for_alembic()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    url, args = get_db_url_and_args_for_alembic()
    connectable = create_engine(
        url,
        connect_args=args,
        poolclass=pool.NullPool,
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