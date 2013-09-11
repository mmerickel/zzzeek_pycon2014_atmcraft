from pyramid.config import Configurator
from pyramid.events import NewRequest, subscriber

from .model.meta import setup_app, Session

@subscriber(NewRequest)
def cleanup_sess(event):
    """Listen for new requests and assign a cleanup handler to each."""

    def remove(request):
        Session.remove()
    event.request.add_finished_callback(remove)

def main(global_config, **settings):
    config = Configurator(settings=settings)

    setup_app(global_config, **settings)

    config.add_route("start_session", "/login")
    config.add_route("withdraw", "/withdraw")
    config.add_route("deposit", "/deposit")
    config.add_route("balance", "/balance")

    config.scan()

    return config.make_wsgi_app()