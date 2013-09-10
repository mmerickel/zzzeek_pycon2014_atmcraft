import unittest

from pyramid import testing
import pyramid.httpexceptions as exc

from . import TransactionalTest, AppTest
from ..model.client import Client, AuthSession
from ..model.account import Account
from ..model.meta import Session
from ..views import auth_on_token, start_session, balance, deposit, withdraw
import datetime
from decimal import Decimal

class _Fixture(object):
    def _auth_fixture(self, created_at=None, client=None, account=None):
        if client is None:
            client = self._client_fixture()
        if account is None:
            account = Account(username="some user")
        auth_session = AuthSession(client, account)
        if created_at is not None:
            auth_session.created_at = created_at
        Session.add(auth_session)
        Session.commit()
        return auth_session

    def _client_fixture(self):
        client = Client(identifier='12345', secret="some secret")
        Session.add(client)
        return client

    def _balance_fixture(self):
        client = self._client_fixture()
        account = Account(username="some user")
        account.add_transaction(client, "checking", Decimal("25.00"))
        account.add_transaction(client, "checking", Decimal("15.00"))
        account.add_transaction(client, "savings", Decimal("50.00"))
        return self._auth_fixture(client=client, account=account)

class AuthTests(_Fixture, TransactionalTest):

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
        self.assertEquals(
            auth_on_token(lambda req: "hi")(request),
            "hi"
        )
        self.assertEquals(request.auth_session, auth_session)

class CreateSessionTest(_Fixture, TransactionalTest):

    def test_login_failed_wrong_pw(self):
        self._client_fixture()
        request = testing.DummyRequest()
        request.params['identifier'] = '12345'
        request.params['secret'] = 'incorrect secret'
        request.params['account_name'] = 'zzzeek_two'

        self.assertRaises(
            exc.HTTPForbidden,
            start_session, request
        )

    def test_login_failed_no_user(self):
        request = testing.DummyRequest()
        request.params['identifier'] = '12345'
        request.params['secret'] = 'some secret'
        request.params['account_name'] = 'zzzeek_two'

        self.assertRaises(
            exc.HTTPForbidden,
            start_session, request
        )

    def test_login(self):
        client = self._client_fixture()
        request = testing.DummyRequest()
        request.params['identifier'] = '12345'
        request.params['secret'] = 'some secret'
        request.params['account_name'] = 'zzzeek_two'

        response = start_session(request)

        auth_session = Session.query(AuthSession).filter_by(client=client).one()
        self.assertEquals(response, {"auth_token": auth_session.token})
        self.assertEquals(auth_session.account.username, "zzzeek_two")

        # second call gives us a new session but same account
        response = start_session(request)
        auth_session_2 = Session.query(AuthSession).\
                            filter_by(client=client).\
                            order_by(AuthSession.id.desc()).first()
        assert auth_session_2 is not auth_session
        assert auth_session_2.account is auth_session.account


class OpTest(_Fixture, TransactionalTest):
    def test_balance(self):
        auth_session = self._balance_fixture()
        request = testing.DummyRequest(params={"auth_token": auth_session.token})
        response = balance(request)
        self.assertEquals(response,
                {"savings": Decimal("50"), "checking": Decimal("40")})

    def test_deposit(self):
        auth_session = self._balance_fixture()
        request = testing.DummyRequest(params={
                                    "auth_token": auth_session.token,
                                    "type": "checking",
                                    "amount": "10.00"
                                    }, method="POST")
        response = deposit(request)
        self.assertEquals(response,
                {"savings": Decimal("50"), "checking": Decimal("50")})


    def test_withdraw(self):
        auth_session = self._balance_fixture()
        request = testing.DummyRequest(params={
                                    "auth_token": auth_session.token,
                                    "type": "checking",
                                    "amount": "10.00"
                                    }, method="POST")
        response = withdraw(request)
        self.assertEquals(response,
                {"savings": Decimal("50"), "checking": Decimal("30")})


    def test_overdraft(self):
        auth_session = self._balance_fixture()
        request = testing.DummyRequest(params={
                                    "auth_token": auth_session.token,
                                    "type": "checking",
                                    "amount": "100.00"
                                    }, method="POST")
        self.assertRaisesRegexp(
            exc.HTTPBadRequest,
            r"overdraft occurred",
            withdraw, request
        )

