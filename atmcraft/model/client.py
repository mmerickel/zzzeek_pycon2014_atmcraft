from .meta import SurrogatePK, Base, Column, String, \
            BcryptType, ReferenceCol, relationship, Session, utcnow
from sqlalchemy.orm import exc
import os
import datetime

class Client(SurrogatePK, Base):
    __tablename__ = 'client'

    identifier = Column(String(32))
    secret = Column(BcryptType)

class AuthSession(SurrogatePK, Base):
    __tablename__ = 'auth_session'

    client_id = ReferenceCol('client')
    account_id = ReferenceCol('account')

    token = Column(String(64), nullable=False)
    client = relationship("Client")
    account = relationship("Account")

    def __init__(self, client, account):
        self.client = client
        self.account = account
        self.token = self._gen_token()

    @classmethod
    def _gen_token(cls):
        return "".join("%.2x" % ord(x) for x in os.urandom(32))

    @classmethod
    def validate_token(cls, auth_token):
        try:
            return Session.query(cls).\
                        filter_by(token=auth_token).\
                        filter(AuthSession.created_at > utcnow() -
                                datetime.timedelta(seconds=360)).one()
        except exc.NoResultFound:
            return None


def console(argv=None):

    def adduser():
        Session.add(Client(identifier=options.username, secret=options.password))
        Session.commit()

    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("config",
                            type=str,
                            help="config file")
    subparsers = parser.add_subparsers()
    subparser = subparsers.add_parser("adduser", help="add a new user")
    subparser.add_argument("username", help="username")
    subparser.add_argument("password", help="password")
    subparser.set_defaults(cmd=adduser)

    options = parser.parse_args(argv)

    from .meta import setup_from_file
    setup_from_file(options.config)
    options.cmd()
