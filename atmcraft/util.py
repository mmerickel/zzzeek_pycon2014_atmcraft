from ConfigParser import SafeConfigParser
from decimal import Decimal
from logging.config import fileConfig

from formencode.validators import Number, Invalid
from pyramid.renderers import JSON

class DecimalNumber(Number):
    """formencode validator for Decimal objects."""

    def _to_python(self, value, state):
        try:
            value = Decimal(value)
            return value
        except ValueError:
            raise Invalid(self.message('number', state), value, state)

def make_json_renderer():
    renderer = JSON(indent=4)
    renderer.add_adapter(Decimal, lambda v, r: str(v))
    return renderer

def setup_from_file(fname):
    """Parse the configuration file and return the settings.

    This will also configure the stdlib logging package.
    """
    fileConfig(fname)

    cfg_parser = SafeConfigParser()
    cfg_parser.read(fname)
    settings = dict(cfg_parser.items('DEFAULT'))
    return settings
