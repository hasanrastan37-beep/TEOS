from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.core.database import Base
from src.core.settings import settings

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_SYNC_URL)
fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    # ... (استاندارد Alembic)
    pass

def run_migrations_online():
    # ... (استاندارد)
    pass

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
