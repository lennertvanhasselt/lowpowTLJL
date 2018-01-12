import unittest

from bitstring import ConstBitStream

from d7a.fs.file_permissions import FilePermissions


class TestPermission(unittest.TestCase):

  def test_parsing(self):
    permission_bytes = [
      0xFC
    ]

    permission = FilePermissions.parse(ConstBitStream(bytes=permission_bytes))

    self.assertEqual(permission.encrypted, True)
    self.assertEqual(permission.executable, True)
    self.assertEqual(permission.user_readable, True)
    self.assertEqual(permission.user_writeable, True)
    self.assertEqual(permission.user_executeable, True)
    self.assertEqual(permission.guest_readable, True)
    self.assertEqual(permission.guest_writeable, False)
    self.assertEqual(permission.guest_executeable, False)

  def test_byte_generation(self):
    p = FilePermissions(encrypted=True, executeable=True, user_readable=True, user_writeable=True, user_executeable=True,
                   guest_readable=True, guest_writeable=False, guest_executeable=False)
    bytes = bytearray(p)
    self.assertEqual(bytes, bytearray([0xFC]))