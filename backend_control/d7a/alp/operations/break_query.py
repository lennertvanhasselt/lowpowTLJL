from d7a.alp.operands.query import QueryOperand
from d7a.alp.operations.operation import Operation


class BreakQuery(Operation):
  def __init__(self, *args, **kwargs):
    self.op = 9
    self.operand_class = QueryOperand
    super(BreakQuery, self).__init__(*args, **kwargs)

