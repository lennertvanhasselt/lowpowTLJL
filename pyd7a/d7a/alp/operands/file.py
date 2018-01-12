# file
# author: Christophe VG <contact@christophe.vg>

# class implementations of File {*} Operands
from d7a.alp.operands.length import Length
from d7a.alp.operands.offset import Offset
from d7a.support.schema import Validatable, Types


class Data(Validatable):

  SCHEMA = [{
    "offset" : Types.OBJECT(Offset),
    "length" : Types.OBJECT(Length),
    "data"   : Types.BYTES()
  }]
  
  def __init__(self, data=[], offset=Offset()):
    self.offset = offset
    self.data   = data
    self.length = Length(len(data))
    super(Data, self).__init__()

  # for consistency with schema, e.g. if using generic attribute conversion, etc
  # @property
  # def length(self):
  #   return len(self.data)

  # the Python way ;-)
  def __len__(self):
    return self.length.value

  def __iter__(self):
    for byte in self.offset: yield byte
    for byte in self.length: yield byte
    for byte in self.data: yield chr(byte)

  def __str__(self):
    return "{}, length={}, data={}".format(self.offset, self.length, self.data)


class DataRequest(Validatable):

  SCHEMA = [{
    "offset" : Types.OBJECT(Offset),
    "length" : Types.OBJECT(Length)
  }]

  def __init__(self, length, offset=Offset()):
    self.offset = offset
    self.length = length
    super(DataRequest, self).__init__()

  def __iter__(self):
    for byte in self.offset: yield byte
    for byte in self.length: yield byte

  def __str__(self):
    return "{}, length={}".format(self.offset, self.length)


class FileIdOperand(Validatable):

  SCHEMA = [{
    "file_id": Types.BYTE()
  }]

  def __init__(self, file_id):
    self.file_id = file_id
    super(FileIdOperand, self).__init__()

  def __iter__(self):
    yield self.file_id

  def __str__(self):
    return "file-id={}".format(self.file_id)