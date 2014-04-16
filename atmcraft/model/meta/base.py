from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import engine_from_config
from zope.sqlalchemy import ZopeTransactionExtension

from .schema import References

def get_engine(settings):
    engine = engine_from_config(settings, 'sqlalchemy.')
    return engine

def get_sessionmaker(settings, zte=True):
    """Configure a sessionmaker for use by requests.

    By default, sessions will attach themselves to the current transaction
    manager. Then can be turned off by setting ``zte=False``.
    """
    engine = get_engine(settings)

    extensions = []
    if zte:
        extensions.append(ZopeTransactionExtension())

    maker = sessionmaker(extension=extensions)
    maker.configure(bind=engine)
    return maker

class Base(References):
    pass

Base = declarative_base(cls=Base)

# establish a constraint naming convention.
# see http://docs.sqlalchemy.org/en/latest/core/constraints.html#configuring-constraint-naming-conventions
#
Base.metadata.naming_convention = {
    "pk": "pk_%(table_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ix": "ix_%(table_name)s_%(column_0_name)s"
}
