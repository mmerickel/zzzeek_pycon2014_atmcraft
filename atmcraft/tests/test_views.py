import unittest

from pyramid import testing

class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_start_session(self):
        from ..views import start_session
        request = testing.DummyRequest()
        info = start_session(request)
        self.assertEqual(info, {'id': '12345'})

