import struct

from d7a.alp.operands.length import Length
from d7a.support.schema import Validatable, Types


class Offset(Validatable):

  SCHEMA = [
    {
      "id"    : Types.BYTE(),
      "offset": Types.OBJECT(Length)
    }
  ]

  def __init__(self, id=0, offset=Length()):
    self.id     = id
    self.offset = offset
    super(Offset, self).__init__()

  @staticmethod
  def parse(s):
    id = s.read("uint:8")
    offset = Length.parse(s)
    return Offset(id=id, offset=offset)

  def __iter__(self):
    yield self.id
    for byte in self.offset: yield byte

  def __str__(self):
    return "file-id={}, offset={}".format(self.id, self.offset)