from ..model.meta import Session
from sqlalchemy import engine_from_config
from logging.config import fileConfig
from ConfigParser import SafeConfigParser
import pkg_resources
import unittest

testing_engine = None

def setup_package():
    fname = pkg_resources.resource_filename("atmcraft", "../development.ini")
    fileConfig(fname)
    config = SafeConfigParser()
    config.read(fname)

    global testing_engine
    settings = dict(config.items("DEFAULT"))
    testing_engine = engine_from_config(settings, 'sqlalchemy.')


class AppTest(unittest.TestCase):
    pass

class TransactionalTest(AppTest):
    """Run tests within a transactional boundary.
    """

    def setUp(self):
        super(TransactionalTest, self).setUp()
        self.connection = testing_engine.connect()
        self.transaction = self.connection.begin()
        self.session = Session(bind=self.connection)

    def tearDown(self):
        Session.remove()

        self.transaction.rollback()
        self.connection.close()
        self.session.close()
        super(TransactionalTest, self).tearDown()

