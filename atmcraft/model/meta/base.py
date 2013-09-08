from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from pyramid.threadlocal import get_current_request
from pyramid.events import NewRequest, subscriber
from sqlalchemy import engine_from_config

def setup_app(global_config, **settings):


    @subscriber(NewRequest)
    def cleanup_sess(event):
        """Listen for new requests and assign a cleanup handler to each."""
        event.request.add_finished_callback(Session.remove)

    # produce a database engine from the config.
    all_settings = global_config.copy()
    all_settings.update(settings)

    engine = engine_from_config(all_settings, "sqlalchemy.")
    Session.configure(bind=engine)

# bind the Session to the current request
Session = scoped_session(sessionmaker(), scopefunc=get_current_request)

Base = declarative_base()

