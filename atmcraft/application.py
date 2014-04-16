from pyramid.config import Configurator

from .util import make_json_renderer

def main(global_config, **app_settings):
    settings = global_config.copy()
    settings.update(app_settings)
    config = Configurator(settings=settings)

    config.include('.model')

    config.add_route("start_session", "/login")
    config.add_route("withdraw", "/withdraw")
    config.add_route("deposit", "/deposit")
    config.add_route("balance", "/balance")

    json_renderer = make_json_renderer()
    config.add_renderer('json', json_renderer)

    config.scan('.views')

    return config.make_wsgi_app()
