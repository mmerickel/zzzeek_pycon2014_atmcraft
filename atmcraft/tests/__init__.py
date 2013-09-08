from ..model.meta import Session, setup_from_file
import pkg_resources
import unittest

def setup_package():
    """Set up configuration and a testing engine.

    Run by nosetests when the test suite starts.

    """

    fname = pkg_resources.resource_filename("atmcraft", "../development.ini")
    setup_from_file(fname)


class AppTest(unittest.TestCase):
    pass

class TransactionalTest(AppTest):
    """Run tests within a transactional boundary.
    """

    def setUp(self):
        super(TransactionalTest, self).setUp()
        from ..model.meta.base import engine
        self.connection = engine.connect()
        self.transaction = self.connection.begin()
        self.session = Session(bind=self.connection)

    def tearDown(self):
        Session.remove()

        self.transaction.rollback()
        self.connection.close()
        self.session.close()
        super(TransactionalTest, self).tearDown()

