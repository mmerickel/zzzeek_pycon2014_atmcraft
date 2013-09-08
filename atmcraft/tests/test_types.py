import unittest
from ..model.meta import Password, BcryptType
import bcrypt

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