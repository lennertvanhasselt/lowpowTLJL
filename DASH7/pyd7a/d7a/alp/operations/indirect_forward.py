from d7a.alp.operands.indirect_interface_operand import IndirectInterfaceOperand
from d7a.alp.operations.operation import Operation


class IndirectForward(Operation):
  def __init__(self, *args, **kwargs):
    self.op     = 51
    self.operand_class = IndirectInterfaceOperand
    super(IndirectForward, self).__init__(*args, **kwargs)