from enum import Enum

from d7a.alp.operands.length import Length
from d7a.alp.operands.offset import Offset
from d7a.support.schema import Validatable, Types

class QueryType(Enum):
  NON_VOID_CHECK = 0
  ARITH_COMP_WITH_ZERO = 1
  ARITH_COMP_WITH_VALUE = 2
  ARITH_COMP_BETWEEN_FILES = 3
  RANGE_COMP = 4
  STRING_TOKEN = 7

class ArithComparisonType(Enum):
  INEQUALITY = 0
  EQUALITY = 1
  LESS_THAN = 2
  LESS_THAN_OR_EQUAL_TO = 3
  GREATER_THAN = 4
  GREATER_THAN_OR_EQUAL_TO = 5

class ArithQueryParams(Validatable):
  SCHEMA = [{
    "signed_data_type": Types.BOOLEAN(),
    "comp_type": Types.OBJECT(ArithComparisonType),
  }]

  def __init__(self, signed_data_type, comp_type):
    self.signed_data_type = signed_data_type
    self.comp_type = comp_type
    super(ArithQueryParams, self).__init__()

  @staticmethod
  def parse(s):
    signed_data_type = s.read("bool")
    comp_type = ArithComparisonType(s.read("uint:3"))
    return ArithQueryParams(signed_data_type, comp_type)

  def __iter__(self):
    byte = self.signed_data_type << 3
    byte += self.comp_type.value
    yield byte

# TODO refactor to support other query types
class QueryOperand(Validatable):
  SCHEMA = [{
    "type": Types.ENUM(type=QueryType),
    "mask_present": Types.BOOLEAN(),
    "params": Types.OBJECT(ArithQueryParams), # TODO other query types
    "compare_length": Types.OBJECT(Length),
    "compare_value": Types.BYTES(),
    "file_a_offset": Types.OBJECT(Offset)
  }]

  def __init__(self, type, mask_present, params, compare_length, compare_value, file_a_offset):
    self.type = type
    self.mask_present = mask_present
    self.params = params
    self.compare_length = compare_length
    self.compare_value = compare_value
    self.file_a_offset = file_a_offset
    super(QueryOperand, self).__init__()

  def __iter__(self):
    byte = self.type.value << 5
    byte += self.mask_present << 4
    byte += bytearray(self.params)[0]
    yield byte
    for byte in self.compare_length: yield byte
    for byte in self.compare_value: yield byte
    for byte in self.file_a_offset: yield byte


  @staticmethod
  def parse(s):
    type = QueryType(s.read("uint:3"))
    assert(type == QueryType.ARITH_COMP_WITH_VALUE) # TODO implement other types
    mask_present = s.read("bool")
    assert(mask_present is False) # TODO implement this
    params = ArithQueryParams.parse(s)
    compare_length = Length.parse(s)
    compare_value = map(ord, s.read("bytes:" + str(compare_length.value)))
    file_a_offset = Offset.parse(s)
    return QueryOperand(type=type, mask_present=mask_present, params=params, compare_length=compare_length,
                        compare_value=compare_value, file_a_offset=file_a_offset)
