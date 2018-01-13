import pprint
import unittest

from bitstring import ConstBitStream

from d7a.alp.operands.length import Length


class TestLength(unittest.TestCase):
  def test_byte_generation(self):
    bytes = bytearray(Length())
    self.assertEqual(len(bytes), 1)
    self.assertEqual(bytes[0], int('00000000', 2))

    bytes = bytearray(Length(value=4))
    self.assertEqual(len(bytes), 1)
    self.assertEqual(bytes[0], int('00000100', 2))

    bytes = bytearray(Length(value=65120))
    self.assertEqual(len(bytes), 3)
    self.assertEqual(bytes[0], int('10000000', 2))
    self.assertEqual(bytes[1], int('11111110', 2))
    self.assertEqual(bytes[2], int('01100000', 2))

  def test_parsing(self):
    length_bytes = [0x01]
    length = Length.parse(ConstBitStream(bytes=length_bytes))
    self.assertEqual(length.value, 1)

    length_bytes = [0x40, 0x41]
    length = Length.parse(ConstBitStream(bytes=length_bytes))
    self.assertEqual(length.value, 65)

    length_bytes = [0xC0, 0x41, 0x10, 0x00]
    length = Length.parse(ConstBitStream(bytes=length_bytes))
    self.assertEqual(length.value, 4263936)