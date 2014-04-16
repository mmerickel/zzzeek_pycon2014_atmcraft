import os
import datetime

from sqlalchemy.orm import exc

from .meta import SurrogatePK, Base, Column, String, BcryptType, \
            utcnow, many_to_one
from .account import Account

class Client(SurrogatePK, Base):
    __tablename__ = 'client'

    identifier = Column(String(32), unique=True)
    secret = Column(BcryptType)

class AuthSession(SurrogatePK, Base):
    __tablename__ = 'auth_session'

    token = Column(String(64), nullable=False)

    client = many_to_one("Client")
    account = many_to_one("Account")

    def __init__(self, client, account):
        self.client = client
        self.account = account
        self.token = self._gen_token()

    @classmethod
    def _gen_token(cls):
        return "".join("%.2x" % ord(x) for x in os.urandom(32))

    @classmethod
    def validate_token(cls, db, auth_token):
        try:
            return db.query(cls).\
                        filter_by(token=auth_token).\
                        filter(AuthSession.created_at > utcnow() -
                                datetime.timedelta(seconds=360)).one()
        except exc.NoResultFound:
            return None

    @classmethod
    def create(cls, db, identifier, secret, account_name):
        try:
            client = db.query(Client).filter_by(identifier=identifier).one()
        except exc.NoResultFound:
            return None
        else:
            if client.secret != secret:
                return None

        account = Account.as_unique(db, account_name)
        auth_session = AuthSession(client, account)
        db.add(auth_session)
        return auth_session

def console(argv=None):
    from argparse import ArgumentParser
    import transaction
    from .meta import get_sessionmaker
    from ..util import setup_from_file

    def adduser(db):
        db.add(Client(identifier=options.username, secret=options.password))

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

    settings = setup_from_file(options.config)
    sessionmaker = get_sessionmaker(settings)

    with transaction.manager:
        db = sessionmaker()
        options.cmd(db)
