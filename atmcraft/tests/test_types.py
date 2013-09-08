import unittest
from ..model.meta import Password, BcryptType, Session, GUID
import bcrypt
from . import TransactionalTest
from sqlalchemy import Table, Column, MetaData, select
import uuid

class GUIDTest(TransactionalTest):
    def setUp(self):
        super(GUIDTest, self).setUp()

        self.guid_table = Table('guid_table', MetaData(),
                Column('guid_value', GUID())
            )

        self.guid_table.create(Session.bind)

    def test_round_trip(self):
        my_guid = uuid.uuid4()
        Session.execute(self.guid_table.insert(), dict(guid_value=my_guid))

        self.assertEquals(
            Session.scalar(select([self.guid_table.c.guid_value])),
            my_guid
        )

class BcryptTypeTest(TransactionalTest):
    def setUp(self):
        super(BcryptTypeTest, self).setUp()

        self.bc_table = Table('bc_table', MetaData(),
                Column('bc_value', BcryptType)
            )

        self.bc_table.create(Session.bind)

    def test_round_trip(self):

        Session.execute(self.bc_table.insert(), dict(bc_value="hello"))

        result = Session.scalar(select([self.bc_table.c.bc_value]))
        self.assertEquals(result, "hello")
        self.assertEquals(result, Password("hello", result))
        self.assertNotEquals(result, "bye")


class PasswordTest(unittest.TestCase):
    def test_password_wrapper_string_cmp(self):
        p1 = Password("abcdef")

        self.assertEquals(p1, "abcdef")
        self.assertNotEquals(p1, "qprzt")

    def test_password_wrapper_pw_cmp(self):
        p1 = Password("abcdef")

        # compare to self
        self.assertEquals(p1, p1)

        # compare to a comparable Password
        self.assertEquals(p1, Password("abcdef", p1))
        self.assertNotEquals(p1, Password("qprzt", p1))

    def test_password_wrapper_conversion(self):
        p1 = Password("abcdef")
        raw = str(p1)
        self.assertEquals(raw, bcrypt.hashpw("abcdef", raw))

    def test_password_type(self):
        self.assertEquals(
            BcryptType().process_bind_param("abcdef", None),
            "abcdef"
        )