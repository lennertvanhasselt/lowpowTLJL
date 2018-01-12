import struct

from d7a.support.schema import Validatable, Types


class Length(Validatable):

  SCHEMA = [
    {
      "length": Types.BITS(2),
      "value": Types.INTEGER(min=0, max=0x3FFFFFFF)
    }
  ]

  def __init__(self, value=0):
    self.value = value
    super(Length, self).__init__()

  @staticmethod
  def parse(s):
    size = s.read("uint:2")  # + 1 = already read
    value = s.read("uint:" + str(6 + (size * 8)))
    return Length(value=value)

  def __iter__(self):
    byte = 0
    size = 1
    if self.value > 0x3F:
      size = 2
    if self.value > 0x3FFF:
      size = 3
    if self.value > 0x3FFFFF:
      size = 4

    byte += (size - 1) << 6

    if size == 1:
      byte += self.value
      yield byte
    else:
      length_bytes = bytearray(struct.pack(">I", self.value))
      if size == 2:   length_bytes = length_bytes[2:]
      elif size == 3: length_bytes = length_bytes[1:]

      byte += length_bytes[0]
      yield byte
      for byte in length_bytes[1:]: yield byte

  def __str__(self):
    return str(self.value)

  def __eq__(self, other):
      if isinstance(other, self.__class__):
        return self.value == other.value
      elif isinstance(other, int):
        return self.value == other
      else:
        return False

  def __ne__(self, other):
      return not self.__eq__(other)