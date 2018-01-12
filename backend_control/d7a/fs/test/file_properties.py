import unittest

from bitstring import ConstBitStream

from d7a.fs.file_properties import FileProperties, ActionCondition, StorageClass


class TestFileProperties(unittest.TestCase):

  def test_parsing(self):
    properties_bytes = [
      0xB3
    ]

    prop = FileProperties.parse(ConstBitStream(bytes=properties_bytes))

    self.assertEqual(prop.act_enabled, True)
    self.assertEqual(prop.act_condition, ActionCondition.WRITE_FLUSH)
    self.assertEqual(prop.storage_class, StorageClass.PERMANENT)

  def test_byte_generation(self):
    prop = FileProperties(act_enabled=True, act_condition=ActionCondition.WRITE, storage_class=StorageClass.VOLATILE)
    bytes = bytearray(prop)
    self.assertEqual(bytes, bytearray([0xA1]))