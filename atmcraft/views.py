from pyramid.view import view_config
import pyramid.httpexceptions as exc
from decorator import decorator
from .model.client import AuthSession
from formencode import Schema, validators
from pyramid_simpleform import Form
from . import util
from .model.meta import commit_on_success
from decimal import Decimal

class DepositWithdrawForm(Schema):
    allow_extra_fields = True
    filter_extra_fields = True
    type = validators.String(max=100)
    amount = util.DecimalNumber(min=Decimal("0"))

@decorator
def auth_on_token(fn, request):
    """Check for a valid AuthSession for this user.

    While Pyramid supplies a much more comprehensive system
    of doing auth/access control, we're keeping it very simple
    here for the purposes of demonstration.

    """
    try:
        auth_token = request.params['auth_token']
    except KeyError:
        raise exc.HTTPForbidden()
    else:
        session = AuthSession.validate_token(auth_token)
        if session is None:
            raise exc.HTTPForbidden()
        request.auth_session = session
        return fn(request)

@view_config(route_name='start_session', renderer='json')
def start_session(request):
    try:
        identifier, secret = request.params['identifier'], request.params['secret']
        account_name = request.params['account_name']
    except KeyError:
        raise exc.HTTPForbidden()
    else:
        session = AuthSession.create(identifier, secret, account_name)
        if session is None:
            raise exc.HTTPForbidden()
        else:
            return {"auth_token": session.token}


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
        auth_session.account.add_transaction(
                        auth_session.client,
                        form.data["type"],
                        Decimal("0") - form.data["amount"]
                        if withdraw else form.data["amount"]
                    )
        return _balances(auth_session.account)
    else:
        raise exc.HTTPBadRequest()

@view_config(route_name='balance', renderer='json')
@auth_on_token
def balance(request):
    auth_session = request.auth_session
    return _balances(auth_session.account)

@view_config(route_name='withdraw', renderer='json')
@auth_on_token
@commit_on_success
def withdraw(request):
    return _withdraw_or_deposit(request, True)

@view_config(route_name='deposit', renderer='json')
@auth_on_token
@commit_on_success
def deposit(request):
    return _withdraw_or_deposit(request, False)
