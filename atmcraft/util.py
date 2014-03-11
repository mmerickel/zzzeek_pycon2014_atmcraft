from formencode.validators import Number, Invalid
from decimal import Decimal
import json

import logging

log = logging.getLogger(__name__)

class DecimalNumber(Number):
    """formencode validator for Decimal objects."""

    def _to_python(self, value, state):
        try:
            value = Decimal(value)
            return value
        except ValueError:
            raise Invalid(self.message('number', state), value, state)


def dumps(obj, default=None, **kw):
    """Json dumps function which includes Decimal processing as well as logging."""

    def default_(obj):
        if isinstance(obj, Decimal):
            return str(obj)
        elif default is not None:
            return default(obj)
        else:
            raise TypeError("value not json encodable: %s" % obj)
    dumped = json.dumps(obj, default=default_, indent=4, **kw)
    log.debug(dumped)
    return dumped
