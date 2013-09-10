from formencode.validators import Number, Invalid
from decimal import Decimal


class DecimalNumber(Number):

    def _to_python(self, value, state):
        try:
            value = Decimal(value)
            return value
        except ValueError:
            raise Invalid(self.message('number', state), value, state)
