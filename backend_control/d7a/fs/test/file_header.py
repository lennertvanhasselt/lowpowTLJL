import struct
import unittest

from bitstring import ConstBitStream

from d7a.fs.file_header import FileHeader
from d7a.fs.file_permissions import FilePermissions
from d7a.fs.file_properties import ActionCondition, StorageClass, FileProperties


class TestFileHeader(unittest.TestCase):

  def test_parsing(self):
    file_header_bytes = [
      0xFC,  # permissions
      0xB3,  # properties
      0x41,  # ALP cmd file id
      0x42,  # interface file id
      0x00, 0x00, 0x01, 0x00,     # file size
      0x00, 0x00, 0x02, 0x00      # allocated size
    ]

    file_header = FileHeader.parse(ConstBitStream(bytes=file_header_bytes))
    permission = file_header.permissions
    self.assertEqual(permission.encrypted, True)
    self.assertEqual(permission.executable, True)
    self.assertEqual(permission.user_readable, True)
    self.assertEqual(permission.user_writeable, True)
    self.assertEqual(permission.user_executeable, True)
    self.assertEqual(permission.guest_readable, True)
    self.assertEqual(permission.guest_writeable, False)
    self.assertEqual(permission.guest_executeable, False)
    prop = file_header.properties
    self.assertEqual(prop.act_enabled, True)
    self.assertEqual(prop.act_condition, ActionCondition.WRITE_FLUSH)
    self.assertEqual(prop.storage_class, StorageClass.PERMANENT)
    self.assertEqual(file_header.alp_command_file_id, 0x41)
    self.assertEqual(file_header.interface_file_id, 0x42)
    self.assertEqual(file_header.file_size, 256)
    self.assertEqual(file_header.allocated_size, 512)


  def test_byte_generation(self):
    file_header = FileHeader(
      permissions=FilePermissions(encrypted=True, executeable=True, user_readable=True, user_writeable=True, user_executeable=True,
                   guest_readable=True, guest_writeable=False, guest_executeable=False),
      properties=FileProperties(act_enabled=True, act_condition=ActionCondition.WRITE_FLUSH, storage_class=StorageClass.PERMANENT),
      alp_command_file_id=0x41,
      interface_file_id=0x42,
      file_size=20,
      allocated_size=40
    )

    bytes = bytearray(file_header)
    self.assertEqual(bytes[0], 0xFC)
    self.assertEqual(bytes[1], 0xB3)
    self.assertEqual(bytes[2], 0x41)
    self.assertEqual(bytes[3], 0x42)
    self.assertEqual(struct.unpack(">I", bytes[4:8])[0], 20)
    self.assertEqual(struct.unpack(">I", bytes[8:12])[0], 40)