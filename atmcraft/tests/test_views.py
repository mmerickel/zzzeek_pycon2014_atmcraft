import unittest

from pyramid import testing
import pyramid.httpexceptions as exc

from . import TransactionalTest, AppTest
from ..model.client import Client, AuthSession
from ..model.account import Account
from ..model.meta import Session
from ..views import auth_on_token
import datetime

class ViewTests(AppTest):

    def test_start_session(self):
        from ..views import start_session
        request = testing.DummyRequest()
        info = start_session(request)
        self.assertEqual(info, {'id': '12345'})

class AuthTests(TransactionalTest):
    def _auth_fixture(self, created_at=None):
        client = Client(identifier='12345', secret="some secret")
        account = Account(username="some user")
        auth_session = AuthSession(client, account)
        if created_at is not None:
            auth_session.created_at = created_at
        Session.add(auth_session)
        Session.commit()
        return auth_session

    def test_auth_not_present(self):
        request = testing.DummyRequest()

        self.assertRaises(
            exc.HTTPForbidden,
            auth_on_token(lambda req: "hi"), request
        )

    def test_auth_timeout(self):
        request = testing.DummyRequest()

        auth_session = self._auth_fixture(
                            created_at=datetime.datetime.utcnow() -
                            datetime.timedelta(seconds=800))
        request.params["auth_token"] = auth_session.token
        self.assertRaises(
            exc.HTTPForbidden,
            auth_on_token(lambda req: "hi"), request
        )

    def test_auth_success(self):
        request = testing.DummyRequest()
        auth_session = self._auth_fixture()
        request.params["auth_token"] = auth_session.token
        auth_on_token(lambda req: "hi")(request)
        self.assertEquals(request.auth_session, auth_session)


