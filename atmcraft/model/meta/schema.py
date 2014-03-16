from sqlalchemy import Column, ForeignKey, Table, DateTime, Integer
from sqlalchemy import event, ForeignKeyConstraint
from sqlalchemy.sql import functions
from sqlalchemy.ext.compiler import compiles

class SurrogatePK(object):
    """A mixin that adds a surrogate integer 'primary key' column named
    ``id`` to any declarative-mapped class."""

    id = Column(Integer, primary_key=True)

class References(object):
    """A mixin that automatically creates foreign key references to
    related classes.

    The :meth:`.References._reference_table` method can be called directly,
    or the :attr:`.References.references` collection can be altered with
    the names of tables to be referenced, which will be handled in the
    ``__declare_first__`` declarative hook.

    The :meth:`.References._reference_table` method works by locating
    the related :class:`.Table` object, then generating locally-mapped columns
    which refer to each column in the primary key of that referenced table.
    It then creates a composite-ready :class:`.ForeignKeyConstraint` object
    referring to those same primary key columns.

    """
    references = ()

    @classmethod
    def __declare_first__(cls):
        for tname in cls.references:
            cls._reference_table(tname)

    @classmethod
    def _reference_table(cls, tname):
        ref_table = cls.metadata.tables[tname]
        for col in ref_table.primary_key:
            setattr(cls, "%s_%s" % (tname, col.name), Column())

        cls.__table__.append_constraint(
                    ForeignKeyConstraint(
                        ["%s_%s" % (tname, col.name) for col in ref_table.primary_key],
                        ["%s.%s" % (tname, col.name) for col in ref_table.primary_key]
                    )
            )


class utcnow(functions.FunctionElement):
    key = 'utcnow'
    type = DateTime(timezone=True)

@compiles(utcnow)
def _default_utcnow(element, compiler, **kw):
    """default compilation handler.

    Note that there is no SQL "utcnow()" function; this is a
    "fake" string so that we can produce SQL strings that are dialect-agnostic,
    such as within tests.

    """
    return "utcnow()"

@compiles(utcnow, 'postgresql')
def _pg_utcnow(element, compiler, **kw):
    """Postgresql-specific compilation handler."""

    return "(CURRENT_TIMESTAMP AT TIME ZONE 'utc')::TIMESTAMP WITH TIME ZONE"


@event.listens_for(Table, "after_parent_attach")
def timestamp_cols(table, metadata):
    from .base import Base

    if metadata is Base.metadata:
        table.append_column(
            Column('created_at',
                        DateTime(timezone=True),
                        nullable=False, default=utcnow())
        )
        table.append_column(
            Column('updated_at',
                        DateTime(timezone=True),
                        nullable=False,
                        default=utcnow(), onupdate=utcnow())
        )

