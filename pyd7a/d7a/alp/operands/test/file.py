# file.py
# author: Christophe VG <contact@christophe.vg>

# unit tests for the D7 File {*} Operands

import unittest

from d7a.alp.operands.file import Data
from d7a.alp.operands.test.offset import TestOffset


class TestData(unittest.TestCase):
  def test_default_data_constructor(self):
    Data()

  def test_data_bad_offset(self):
    def bad(): Data(Data())
    self.assertRaises(ValueError, bad)

  def test_data_length(self):
    d = Data(data=[0xd7, 0x04, 0x00])
    self.assertEqual(d.length.value, 3)
    self.assertEqual(len(d),   3)

  def test_byte_generation(self):
    bytes = bytearray(Data())
    self.assertEqual(len(bytes), 3)
    self.assertEqual(bytes[0], int('00000000', 2)) # offset
    self.assertEqual(bytes[1], int('00000000', 2)) # offset
    self.assertEqual(bytes[2], int('00000000', 2))

    bytes = bytearray(Data(data=[0x01,0x02,0x03,0x04]))
    self.assertEqual(len(bytes), 7)
    self.assertEqual(bytes[0], int('00000000', 2)) # offset
    self.assertEqual(bytes[1], int('00000000', 2)) # offset
    self.assertEqual(bytes[2], int('00000100', 2)) # length = 4
    self.assertEqual(bytes[3], int('00000001', 2))
    self.assertEqual(bytes[4], int('00000010', 2))
    self.assertEqual(bytes[5], int('00000011', 2))
    self.assertEqual(bytes[6], int('00000100', 2))
    
if __name__ == '__main__':
  for case in [TestOffset, TestData]:
    suite = unittest.TestLoader().loadTestsFromTestCase(case)
    unittest.TextTestRunner(verbosity=2).run(suite)
