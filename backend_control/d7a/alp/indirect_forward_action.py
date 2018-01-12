from d7a.alp.action import Action
from d7a.alp.operands.indirect_interface_operand import IndirectInterfaceOperand
from d7a.alp.operations.indirect_forward import IndirectForward
from d7a.alp.operations.nop import NoOperation
from d7a.support.schema import Types


class IndirectForwardAction(Action):
  SCHEMA = [{
    "overload" : Types.BOOLEAN(),
    "resp"     : Types.BOOLEAN(),
    "op"       : Types.BITS(6),
    "operation": Types.OBJECT(IndirectForward),
    "operand"  : Types.OBJECT(IndirectInterfaceOperand)  # TODO for now only D7 interface is supported
  }]

  def __init__(self, overload=False, resp=False, operation=NoOperation()):
    self.overload = overload
    self.resp = resp
    super(IndirectForwardAction, self).__init__(operation)

  def __iter__(self):
    byte = 0
    if self.overload: byte |= 1 << 7
    if self.resp:  byte |= 1 << 6
    byte += self.op
    yield byte

    for byte in self.operation: yield byte
