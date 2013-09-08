from sqlalchemy import Integer, String, Numeric
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID

import uuid
import bcrypt

Amount = Numeric(8, 2)

class Password(str):
    """Coerce a string to a bcrypt password.

    Rationale: for an easy string comparison,
    so we can say ``some_password == 'hello123'``

    """

    def __new__(cls, value, salt=None):
        return str.__new__(cls, bcrypt.hashpw(value, salt or bcrypt.gensalt(4)))

    def __eq__(self, other):
        if not isinstance(other, Password):
            other = bcrypt.hashpw(other, self)
        return str.__eq__(self, other)

class BcryptType(TypeDecorator):
    """Coerce strings to bcrypted Password objects for the database.
    """

    impl = String(128)

    def process_bind_param(self, value, dialect):
        return Password(value)

    def __repr__(self):
        return "BcryptType()"

class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses Postgresql's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.

    """
    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value)
            else:
                # hexstring
                return "%.32x" % value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)

