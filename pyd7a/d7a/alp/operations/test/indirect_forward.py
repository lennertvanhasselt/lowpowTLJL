import unittest

from d7a.alp.operands.indirect_interface_operand import IndirectInterfaceOperand
from d7a.alp.operations.indirect_forward import IndirectForward
from d7a.d7anp.addressee import Addressee


class TestIndirectForward(unittest.TestCase):
  def test_byte_generation(self):
    indirect_forward_action = IndirectForward(
      operand=IndirectInterfaceOperand(
        interface_file_id=0x40,
        interface_configuration_overload=None
      )
    )

    bytes = bytearray(indirect_forward_action)
    self.assertEqual(len(bytes), 1)
    self.assertEqual(bytes[0], 0x40)

  def test_byte_generation_with_overload(self):
    indirect_forward_action = IndirectForward(
      operand=IndirectInterfaceOperand(
        interface_file_id=0x40,
        interface_configuration_overload=Addressee()
      )
    )

    bytes = bytearray(indirect_forward_action)
    self.assertEqual(len(bytes), 3)
    self.assertEqual(bytes[0], 0x40)
