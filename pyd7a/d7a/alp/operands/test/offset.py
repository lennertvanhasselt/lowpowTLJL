import pprint
import unittest

from bitstring import ConstBitStream

from d7a.alp.operands.length import Length
from d7a.alp.operands.offset import Offset


class TestOffset(unittest.TestCase):
  def test_byte_generation(self):
    bytes = bytearray(Offset())
    self.assertEqual(len(bytes), 2)
    self.assertEqual(bytes[0], int('00000000', 2))
    self.assertEqual(bytes[1], int('00000000', 2))

    bytes = bytearray(Offset(id=0xFF))
    self.assertEqual(len(bytes), 2)
    self.assertEqual(bytes[0], int('11111111', 2))
    self.assertEqual(bytes[1], int('00000000', 2))

    bytes = bytearray(Offset(offset=Length(65120)))
    self.assertEqual(len(bytes), 4)
    self.assertEqual(bytes[0], int('00000000', 2))
    self.assertEqual(bytes[1], int('10000000', 2))
    self.assertEqual(bytes[2], int('11111110', 2))
    self.assertEqual(bytes[3], int('01100000', 2))

  def test_parse(self):
    offset_bytes = [0x20, 0x01]
    offset = Offset.parse(ConstBitStream(bytes=offset_bytes))
    self.assertEqual(offset.id, 32)
    self.assertEqual(offset.offset.value, 1)

  def test_parse_two_bytes(self):
    offset_bytes = [0x20, 0x40, 0x41]
    offset = Offset.parse(ConstBitStream(bytes=offset_bytes))
    self.assertEqual(offset.offset.value, 65)

  def test_parse_three_bytes(self):
    offset_bytes = [0x20, 0x40, 0x41]
    offset = Offset.parse(ConstBitStream(bytes=offset_bytes))
    self.assertEqual(offset.offset.value, 65)

  def test_to_str(self):
    Offset().__str__()