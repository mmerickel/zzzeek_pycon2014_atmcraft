from formencode.validators import Number, Invalid
from decimal import Decimal
import json

class DecimalNumber(Number):

    def _to_python(self, value, state):
        try:
            value = Decimal(value)
            return value
        except ValueError:
            raise Invalid(self.message('number', state), value, state)


def dumps(obj, default=None, **kw):
    def default_(obj):
        if isinstance(obj, Decimal):
            return str(obj)
        elif default is not None:
            return default(obj)
        else:
            raise TypeError("value not json encodable: %s" % obj)
    return json.dumps(obj, default=default_, **kw)
