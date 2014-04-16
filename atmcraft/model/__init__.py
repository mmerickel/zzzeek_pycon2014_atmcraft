from . import meta
from . import account, client

def includeme(config):
    settings = config.get_settings()

    config.include('pyramid_tm')

    sessionmaker = meta.get_sessionmaker(settings)
    config.registry['dbsession'] = sessionmaker
    config.add_request_method(lambda request: sessionmaker(), 'db', reify=True)
