from pyramid.view import view_config
import pyramid.httpexceptions as exc
from decorator import decorator
from .model.client import AuthSession

@decorator
def auth_on_token(fn, request):
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
    return {"id": "12345"}


@view_config(route_name='withdraw', renderer='json')
@auth_on_token
def withdraw(request):
    return {"id": "12345"}

@view_config(route_name='deposit', renderer='json')
@auth_on_token
def deposit(request):
    return {"id": "12345"}

