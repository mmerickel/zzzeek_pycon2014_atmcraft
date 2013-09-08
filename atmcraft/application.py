from pyramid.config import Configurator

def main(global_config, **settings):
    config = Configurator(settings=settings)
#    config.add_static_view('static', 'static', cache_max_age=3600)

    config.add_route("start_session", "/login")
    config.add_route("withdraw", "/withdraw")
    config.add_route("deposit", "/deposit")

    config.scan()

    from sqlalchemy.orm import configure_mappers
    configure_mappers()

    return config.make_wsgi_app()