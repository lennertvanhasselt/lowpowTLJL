
from d7a.alp.operations.operation import Operation
from d7a.alp.operands.file import DataRequest, FileIdOperand


class ReadFileData(Operation):
  def __init__(self, *args, **kwargs):
    self.op     = 1
    self.operand_class = DataRequest
    super(ReadFileData, self).__init__(*args, **kwargs)


class ReadFileHeader(Operation):
  def __init__(self, *args, **kwargs):
    self.op = 2
    self.operand_class = FileIdOperand
    super(ReadFileHeader, self).__init__(*args, **kwargs)

