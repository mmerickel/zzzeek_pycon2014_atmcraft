from sqlalchemy import Column, ForeignKey

def ReferenceCol(tablename, nullable=False, **kw):
    return Column(ForeignKey("%s.id" % tablename), nullable=nullable, **kw)

