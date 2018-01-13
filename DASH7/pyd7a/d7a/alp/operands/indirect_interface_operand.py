from d7a.alp.interface import InterfaceType
from d7a.d7anp.addressee import Addressee
from d7a.sp.configuration import Configuration
from d7a.support.schema import Validatable, Types


class IndirectInterfaceOperand(Validatable):

  SCHEMA = [{
    "interface_file_id"        : Types.INTEGER(min=0x40, max=0xFF),
    "interface_configuration_overload"    : Types.OBJECT(Addressee, nullable=True) # TODO assuming D7ASP interface
  }]

  def __init__(self, interface_file_id, interface_configuration_overload):
    self.interface_file_id = interface_file_id
    self.interface_configuration_overload = interface_configuration_overload
    super(IndirectInterfaceOperand, self).__init__()

  def __iter__(self):
    yield self.interface_file_id
    if self.interface_configuration_overload is not None:
      for byte in self.interface_configuration_overload: yield byte

  def __str__(self):
    return "interface-file-id={}, configuration-overload={}".format(self.interface_file_id, self.interface_configuration_overload)
