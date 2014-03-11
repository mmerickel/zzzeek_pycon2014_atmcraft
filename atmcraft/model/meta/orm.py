from sqlalchemy.orm import relationship, mapper
from .schema import ReferenceCol
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import event


def many_to_one(clsname, **kw):
    """Use an event to build a many-to-one relationship on a class."""

    @declared_attr
    def m2o(cls):

        @event.listens_for(mapper, "before_configured", once=True)
        def setup_fk():
            refernced_cls = cls._decl_class_registry[clsname]
            tablename = refernced_cls.__table__.name
            if not hasattr(cls, "%s_id" % tablename):
                col = ReferenceCol(tablename)
                setattr(cls, "%s_id" % tablename, col)

        return relationship(clsname, **kw)
    return m2o

def one_to_many(clsname, **kw):
    """Use an event to build a one-to-many relationship on a class."""

    @declared_attr
    def o2m(cls):

        @event.listens_for(mapper, "before_configured", once=True)
        def setup_fk():
            refernced_cls = cls._decl_class_registry[clsname]
            tablename = cls.__table__.name
            if not hasattr(refernced_cls, "%s_id" % tablename):
                col = ReferenceCol(tablename)
                setattr(refernced_cls, "%s_id" % tablename, col)

        return relationship(clsname, **kw)
    return o2m


class UniqueMixin(object):
    """Unique object mixin.

    Allows an object to be returned or created as needed based on
    criterion.

    .. seealso::

        http://www.sqlalchemy.org/trac/wiki/UsageRecipes/UniqueObject

    """
    @classmethod
    def unique_hash(cls, *arg, **kw):
        raise NotImplementedError()

    @classmethod
    def unique_filter(cls, query, *arg, **kw):
        raise NotImplementedError()

    @classmethod
    def as_unique(cls, session, *arg, **kw):

        hashfunc = cls.unique_hash
        queryfunc = cls.unique_filter
        constructor = cls

        if 'unique_cache' not in session.info:
            session.info['unique_cache'] = cache = {}
        else:
            cache = session.info['unique_cache']

        key = (cls, hashfunc(*arg, **kw))
        if key in cache:
            return cache[key]
        else:
            with session.no_autoflush:
                q = session.query(cls)
                q = queryfunc(q, *arg, **kw)
                obj = q.first()
                if not obj:
                    obj = constructor(*arg, **kw)
                    session.add(obj)
            cache[key] = obj
            return obj
