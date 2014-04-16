import datetime
from decimal import Decimal

from pyramid import testing
from pyramid import httpexceptions as exc

from ..model.client import Client, AuthSession
from ..model.account import Account
from ..views import auth_on_token, start_session, balance, deposit, withdraw
from . import TransactionalTest

class _TransactionalFixture(TransactionalTest):

    def _auth_fixture(self, created_at=None, client=None, account=None):
        if client is None:
            client = self._client_fixture()

        if account is None:
            account = Account(username="some user")
            self.db.add(account)

        auth_session = AuthSession(client, account)
        if created_at is not None:
            auth_session.created_at = created_at

        self.db.add(auth_session)
        return auth_session

    def _client_fixture(self):
        client = Client(identifier='12345', secret="some secret")
        self.db.add(client)
        return client

    def _balance_fixture(self):
        client = self._client_fixture()
        account = Account(username="some user")
        self.db.add(account)

        account.add_transaction(client, "checking", Decimal("25.00"))
        account.add_transaction(client, "checking", Decimal("15.00"))
        account.add_transaction(client, "savings", Decimal("50.00"))
        return self._auth_fixture(client=client, account=account)


class AuthTests(_TransactionalFixture):

    def test_auth_not_present(self):
        request = testing.DummyRequest()

        self.assertRaises(
            exc.HTTPForbidden,
            auth_on_token(lambda ctx, req: "hi"), None, request
        )

    def test_auth_timeout(self):
        request = testing.DummyRequest()

        auth_session = self._auth_fixture(
                            created_at=datetime.datetime.utcnow() -
                            datetime.timedelta(seconds=800))

        request.params["auth_token"] = auth_session.token
        request.db = self.db
        self.assertRaises(
            exc.HTTPForbidden,
            auth_on_token(lambda ctx, req: "hi"), None, request
        )

    def test_auth_success(self):
        request = testing.DummyRequest()
        auth_session = self._auth_fixture()
        request.params["auth_token"] = auth_session.token
        request.db = self.db
        self.assertEquals(
            auth_on_token(lambda ctx, req: "hi")(None, request),
            "hi"
        )
        self.assertEquals(request.auth_session, auth_session)

class CreateSessionTest(_TransactionalFixture):

    def test_login_failed_wrong_pw(self):
        self._client_fixture()
        request = testing.DummyRequest(method="POST")
        request.params['identifier'] = '12345'
        request.params['secret'] = 'incorrect secret'
        request.params['account_name'] = 'zzzeek_two'
        request.db = self.db

        self.assertRaises(
            exc.HTTPForbidden,
            start_session, request
        )

    def test_login_failed_no_user(self):
        request = testing.DummyRequest(method="POST")
        request.params['identifier'] = '12345'
        request.params['secret'] = 'some secret'
        request.params['account_name'] = 'zzzeek_two'
        request.db = self.db

        self.assertRaises(
            exc.HTTPForbidden,
            start_session, request
        )

    def test_login_failed_wrong_method(self):
        self._client_fixture()
        request = testing.DummyRequest(method="GET")
        request.params['identifier'] = '12345'
        request.params['secret'] = 'some secret'
        request.params['account_name'] = 'zzzeek_two'
        request.db = self.db

        self.assertRaises(
            exc.HTTPForbidden,
            start_session, request
        )

    def test_login_failed_invalid_identifier(self):
        self._client_fixture()
        request = testing.DummyRequest(method="POST")
        request.params['identifier'] = '12346'
        request.params['secret'] = 'some secret'
        request.params['account_name'] = 'zzzeek_two'
        request.db = self.db

        self.assertRaises(
            exc.HTTPForbidden,
            start_session, request
        )

    def test_login(self):
        client = self._client_fixture()
        request = testing.DummyRequest(method="POST")
        request.params['identifier'] = '12345'
        request.params['secret'] = 'some secret'
        request.params['account_name'] = 'zzzeek_two'
        request.db = self.db

        response = start_session(request)

        auth_session = self.db.query(AuthSession).filter_by(client=client).one()
        self.assertEquals(response, {"auth_token": auth_session.token})
        self.assertEquals(auth_session.account.username, "zzzeek_two")

        # second call gives us a new session but same account
        response = start_session(request)
        auth_session_2 = self.db.query(AuthSession).\
                            filter_by(client=client).\
                            order_by(AuthSession.id.desc()).first()

        assert auth_session_2 is not auth_session
        assert auth_session_2.account is auth_session.account


class OpTest(_TransactionalFixture):
    def test_balance(self):
        auth_session = self._balance_fixture()
        request = testing.DummyRequest(method="GET")
        request.auth_session = auth_session
        response = balance(request)
        self.assertEquals(response,
                {"savings": Decimal("50"), "checking": Decimal("40")})

    def test_empty_deposit(self):
        auth_session = self._auth_fixture()

        request = testing.DummyRequest(params={
                                    "type": "checking",
                                    "amount": "10.00"
                                    }, method="POST")
        request.auth_session = auth_session
        response = deposit(request)
        self.assertEquals(response,
                {"checking": Decimal("10")})

    def test_deposit(self):
        auth_session = self._balance_fixture()
        request = testing.DummyRequest(params={
                                    "type": "checking",
                                    "amount": "10.00"
                                    }, method="POST")
        request.auth_session = auth_session
        response = deposit(request)
        self.assertEquals(response,
                {"savings": Decimal("50"), "checking": Decimal("50")})


    def test_withdraw(self):
        auth_session = self._balance_fixture()
        request = testing.DummyRequest(params={
                                    "type": "checking",
                                    "amount": "10.00"
                                    }, method="POST")
        request.auth_session = auth_session
        response = withdraw(request)
        self.assertEquals(response,
                {"savings": Decimal("50"), "checking": Decimal("30")})


    def test_overdraft(self):
        auth_session = self._balance_fixture()
        request = testing.DummyRequest(params={
                                    "type": "checking",
                                    "amount": "100.00"
                                    }, method="POST")
        request.auth_session = auth_session
        self.assertRaisesRegexp(
            exc.HTTPBadRequest,
            r"overdraft occurred",
            withdraw, request
        )

