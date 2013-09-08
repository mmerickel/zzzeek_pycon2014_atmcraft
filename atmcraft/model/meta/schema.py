from sqlalchemy import Column, ForeignKey, Table, ForeignKeyConstraint, \
                    PrimaryKeyConstraint, UniqueConstraint, Index, DateTime
from sqlalchemy import event
from sqlalchemy.sql import functions
from sqlalchemy.ext.compiler import compiles

def ReferenceCol(tablename, nullable=False, **kw):
    return Column(ForeignKey("%s.id" % tablename), nullable=nullable, **kw)

class utcnow(functions.FunctionElement):
    key = 'utcnow'
    type = DateTime(timezone=True)

@compiles(utcnow, 'postgresql')
def _pg_utcnow(element, compiler, **kw):
    return "(CURRENT_TIMESTAMP AT TIME ZONE 'utc')::TIMESTAMP WITH TIME ZONE"



@event.listens_for(Table, "after_parent_attach")
def timestamp_cols(table, metadata):
    if not table.name.startswith('alembic'):
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

@event.listens_for(PrimaryKeyConstraint, "after_parent_attach")
def pk_const_name(const, table):
    const.name = "pk_%s" % (table.name, )

@event.listens_for(ForeignKeyConstraint, "after_parent_attach")
def fk_const_name(const, table):
    fk = list(const.elements)[0]
    reftable, refcol = fk.target_fullname.split(".")
    const.name = "fk_%s_%s_%s" % (table.name,
                                fk.parent.name,
                                reftable
                                )

@event.listens_for(UniqueConstraint, "after_parent_attach")
def unique_const_name(const, table):
    const.name = "uq_%s_%s" % (
        table.name,
        list(const.columns)[0].name
    )

@event.listens_for(Index, "after_parent_attach")
def index_const_name(const, table):
    const.name = "ix_%s_%s" % (
        table.name,
        list(const.columns)[0].name
    )
