from sqlalchemy import create_engine

# If we're here, config must've been loaded
from inbox.config import config, db_uri
assert config
from inbox.sqlalchemy_ext.util import ForceStrictMode


def main_engine(pool_size=None, max_overflow=5):
    db_pool_size = pool_size or config.get_required('DB_POOL_SIZE')

    engine = create_engine(db_uri(),
                           listeners=[ForceStrictMode()],
                           isolation_level='READ COMMITTED',
                           echo=False,
                           pool_size=db_pool_size,
                           pool_recycle=3600,
                           max_overflow=max_overflow,
                           connect_args={'charset': 'utf8mb4'})
    return engine


def init_db(engine):
    """
    Make the tables.

    This is called only from bin/create-db, which is run during setup.
    Previously we allowed this to run everytime on startup, which broke some
    alembic revisions by creating new tables before a migration was run.
    From now on, we should ony be creating tables+columns via SQLalchemy *once*
    and all subsequent changes done via migration scripts.

    """
    from inbox.models.base import MailSyncBase

    MailSyncBase.metadata.create_all(engine)
