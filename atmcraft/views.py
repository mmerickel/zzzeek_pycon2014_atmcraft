from pyramid.view import view_config

@view_config(route_name='start_session', renderer='json')
def start_session(request):
    return {"id": "12345"}


@view_config(route_name='withdraw', renderer='json')
def withdraw(request):
    return {"id": "12345"}

@view_config(route_name='deposit', renderer='json')
def deposit(request):
    return {"id": "12345"}

