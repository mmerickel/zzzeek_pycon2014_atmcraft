import mock
import os
import pkg_resources
import unittest

from sqlalchemy.orm import Session

from ..model.meta import get_engine
from ..util import setup_from_file
from ._mock_session import MockSession

config_file = (
    os.environ.get('TEST_INI') or
    pkg_resources.resource_filename("atmcraft", "../development.ini"))

class AppTest(unittest.TestCase):
    settings = setup_from_file(config_file)

class TransactionalTest(AppTest):
    """Run tests against a relational database within a transactional boundary.
    """

    def setUp(self):
        super(TransactionalTest, self).setUp()
        engine = get_engine(self.settings)
        self.connection = engine.connect()
        self.transaction = self.connection.begin()
        self.db = Session(bind=self.connection)

    def tearDown(self):
        self.transaction.rollback()
        self.connection.close()
        self.db.close()
        super(TransactionalTest, self).tearDown()


class MockDatabaseTest(AppTest):
    """Run tests against a mock query system."""

    def setUp(self):
        super(MockDatabaseTest, self).setUp()
        self.db = MockSession()

        self.object_session_patcher = mock.patch(
            'atmcraft.model.account.object_session')
        self.object_session = self.object_session_patcher.start()
        self.object_session.return_value = self.db

    def tearDown(self):
        super(MockDatabaseTest, self).tearDown()
        self.object_session_patcher.stop()
