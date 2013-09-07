class Client(SurrogatePK, Base):
    __tablename__ = 'client'

    identifier = Column(String(32))
    secret = Column(BcryptType())

