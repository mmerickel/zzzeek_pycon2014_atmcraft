from pyramid import testing
import pyramid.httpexceptions as exc

from . import MockDatabaseTest
from ..model.client import Client, AuthSession
from ..model.account import Account, BalanceType
from ..model.meta import Session, utcnow
from ..views import auth_on_token, start_session, balance, deposit, withdraw
import datetime
from sqlalchemy.orm.exc import NoResultFound
from decimal import Decimal

class _MockFixture(MockDatabaseTest):
    def setUp(self):
        super(_MockFixture, self).setUp()
        self._default_lookups()

    def _default_lookups(self):
        # establish BalanceType lookups which will begin as
        # "not found"; the "unique object" utilitiy will
        # create them.
        Session.query(BalanceType).\
                    filter(BalanceType.name == "checking").\
                    first.return_value = None
        Session.query(BalanceType).\
                    filter(BalanceType.name == "savings").\
                    first.return_value = None

        # no Client by default
        Session.query(Client).filter_by(identifier="12345").\
                one.side_effect = NoResultFound

        # no result for 12346
        Session.query(Client).filter_by(identifier="12346").\
                one.side_effect = NoResultFound

        # start with no Account found for zzzeek_two, some user
        Session.query(Account).\
            filter(Account.username == "zzzeek_two").\
            first.return_value = None
        Session.query(Account).\
            filter(Account.username == "some user").\
            first.return_value = None

    def _auth_fixture(self, created_at=None, client=None, account=None):
        if client is None:
            client = self._client_fixture()

        if account is None:
            account = Account(username="some user")

        auth_session = AuthSession(client, account)
        if created_at is not None:
            auth_session.created_at = created_at

        # establish DB lookup for AuthSession...
        validate_session_q = Session.query(AuthSession).\
                    filter_by(token=auth_session.token).\
                    filter(AuthSession.created_at > utcnow() -
                            datetime.timedelta(seconds=360))

        # the query checks for timeout, so work that into the
        # result
        if created_at is not None and \
            datetime.datetime.utcnow() - created_at > datetime.timedelta(seconds=360):
            validate_session_q.one.side_effect = NoResultFound
        else:
            validate_session_q.one.return_value = auth_session

        return auth_session

    def _client_fixture(self):
        # new Client object
        client = Client(identifier='12345', secret="some secret")

        # establish it as able to be looked up
        q = Session.query(Client).filter_by(identifier="12345")
        q.one.return_value = client
        q.one.side_effect = None  # cancel out existing side effect

        return client

    def _balance_fixture(self):
        client = self._client_fixture()
        account = Account(username="some user")
        account.add_transaction(client, "checking", Decimal("25.00"))
        account.add_transaction(client, "checking", Decimal("15.00"))
        account.add_transaction(client, "savings", Decimal("50.00"))
        return self._auth_fixture(client=client, account=account)


class AuthTests(_MockFixture):

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

class CreateSessionTest(_MockFixture):

    def test_login_failed_wrong_pw(self):
        self._client_fixture()
        request = testing.DummyRequest(method="POST")
        request.params['identifier'] = '12345'
        request.params['secret'] = 'incorrect secret'
        request.params['account_name'] = 'zzzeek_two'

        self.assertRaises(
            exc.HTTPForbidden,
            start_session, request
        )

    def test_login_failed_no_user(self):
        request = testing.DummyRequest(method="POST")
        request.params['identifier'] = '12345'
        request.params['secret'] = 'some secret'
        request.params['account_name'] = 'zzzeek_two'

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

        self.assertRaises(
            exc.HTTPForbidden,
            start_session, request
        )

    def test_login(self):
        self._client_fixture()
        request = testing.DummyRequest(method="POST")
        request.params['identifier'] = '12345'
        request.params['secret'] = 'some secret'
        request.params['account_name'] = 'zzzeek_two'

        response = start_session(request)

        account = Session().add.mock_calls[0][1][0]
        auth_session = Session().add.mock_calls[1][1][0]
        self.assertEquals(response, {"auth_token": auth_session.token})
        self.assertEquals(auth_session.account.username, "zzzeek_two")
        assert auth_session.account is account

        # second call gives us a new session but same account
        response = start_session(request)
        auth_session_2 = Session().add.mock_calls[2][1][0]

        assert auth_session_2 is not auth_session
        assert auth_session_2.account is auth_session.account


class OpTest(_MockFixture):
    def test_balance(self):
        auth_session = self._balance_fixture()
        request = testing.DummyRequest(params={"auth_token": auth_session.token},
                                            method="GET")
        response = balance(request)
        self.assertEquals(response,
                {"savings": Decimal("50"), "checking": Decimal("40")})

    def test_empty_deposit(self):
        auth_session = self._auth_fixture()

        request = testing.DummyRequest(params={
                                    "auth_token": auth_session.token,
                                    "type": "checking",
                                    "amount": "10.00"
                                    }, method="POST")
        response = deposit(request)
        self.assertEquals(response,
                {"checking": Decimal("10")})

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

