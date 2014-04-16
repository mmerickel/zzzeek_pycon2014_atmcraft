from decimal import Decimal

from decorator import decorator
from formencode import Schema, validators
from pyramid import httpexceptions as exc
from pyramid.view import view_config
from pyramid_simpleform import Form

from .model.client import AuthSession
from . import util

log = __import__('logging').getLogger(__name__)

class StartSessionForm(Schema):
    identifier = validators.String(max=100)
    secret = validators.String(max=100)
    account_name = validators.String(max=100)

class DepositWithdrawForm(Schema):
    allow_extra_fields = True
    filter_extra_fields = True
    type = validators.String(max=100)
    amount = util.DecimalNumber(min=Decimal("0"))

@decorator
def auth_on_token(fn, context, request):
    """Check for a valid AuthSession for this user.

    While Pyramid supplies a much more comprehensive system
    of doing auth/access control, we're keeping it very simple
    here for the purposes of demonstration.

    We will attach this to views using
    ``view_config(..., decorator=auth_on_token)``. This syntax allows us to
    attach the decorator to class-based and function-based views with the same
    (context, request) signature on the decorator.

    """
    try:
        auth_token = request.params['auth_token']
    except KeyError:
        raise exc.HTTPForbidden("auth_token is required")
    else:
        session = AuthSession.validate_token(request.db, auth_token)
        if session is None:
            raise exc.HTTPForbidden("no session for given auth_token")
        request.auth_session = session
        return fn(context, request)

@view_config(route_name='start_session', renderer='json')
def start_session(request):
    form = Form(request,
                schema=StartSessionForm())
    if form.validate():
        identifier = form.data["identifier"]
        secret = form.data["secret"]
        account_name = form.data["account_name"]
        db = request.db
        session = AuthSession.create(db, identifier, secret, account_name)
        if session is None:
            raise exc.HTTPForbidden()
        else:
            log.debug("new auth session for client %s username %s",
                        identifier, account_name)
            return {"auth_token": session.token}
    else:
        raise exc.HTTPForbidden()

@view_config(route_name='balance', renderer='json', decorator=auth_on_token)
def balance(request):
    auth_session = request.auth_session
    return _balances(auth_session.account)

@view_config(route_name='withdraw', renderer='json', decorator=auth_on_token)
def withdraw(request):
    return _withdraw_or_deposit(request, True)

@view_config(route_name='deposit', renderer='json', decorator=auth_on_token)
def deposit(request):
    return _withdraw_or_deposit(request, False)


def _balances(account):
    return dict(
                (balance_type.name, account_balance.balance)
                for balance_type, account_balance
                in account.balances.items()
            )

def _withdraw_or_deposit(request, withdraw):
    form = Form(request,
                schema=DepositWithdrawForm())
    if form.validate():
        auth_session = request.auth_session
        try:
            auth_session.account.add_transaction(
                            auth_session.client,
                            form.data["type"],
                            Decimal("0") - form.data["amount"]
                            if withdraw else form.data["amount"]
                        )
            log.debug("%s %d of type %s",
                        "withdraw" if withdraw else "deposit",
                        form.data["amount"], form.data["type"])
        except ValueError as err:
            raise exc.HTTPBadRequest(str(err))

        return _balances(auth_session.account)
    else:
        raise exc.HTTPBadRequest()
