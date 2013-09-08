from pyramid.view import view_config
import pyramid.httpexceptions as exc
from decorator import decorator
from .model.client import AuthSession

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


@view_config(route_name='withdraw', renderer='json')
@auth_on_token
def withdraw(request):
    return {"id": "12345"}

@view_config(route_name='deposit', renderer='json')
@auth_on_token
def deposit(request):
    return {"id": "12345"}

