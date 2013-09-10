from pyramid.config import Configurator
from .model.meta import setup_app

def main(global_config, **settings):
    config = Configurator(settings=settings)

    setup_app(global_config, **settings)

    config.add_route("start_session", "/login")
    config.add_route("withdraw", "/withdraw")
    config.add_route("deposit", "/deposit")
    config.add_route("balance", "/balance")

    config.scan()

    return config.make_wsgi_app()