import struct

from d7a.fs.file_permissions import FilePermissions
from d7a.fs.file_properties import FileProperties
from d7a.support.schema import Validatable, Types


class FileHeader(Validatable):
  SCHEMA = [{
    "permissions": Types.OBJECT(FilePermissions),
    "properties": Types.OBJECT(FileProperties),
    "alp_command_file_id": Types.BYTE(),
    "interface_file_id": Types.BYTE(),
    "file_size": Types.INTEGER(min=0, max=0xFFFFFFFF),
    "allocated_size": Types.INTEGER(min=0, max=0xFFFFFFFF)
  }]

  def __init__(self, permissions, properties, alp_command_file_id, interface_file_id, file_size, allocated_size):
    self.permissions = permissions
    self.properties = properties
    self.alp_command_file_id = alp_command_file_id
    self.interface_file_id = interface_file_id
    self.file_size = file_size
    self.allocated_size = allocated_size
    Validatable.__init__(self)

  @staticmethod
  def parse(s):
    permissions = FilePermissions.parse(s)
    properties = FileProperties.parse(s)
    alp_command_file_id = s.read("uint:8")
    interface_file_id = s.read("uint:8")
    file_size = s.read("uint:32")
    allocated_size = s.read("uint:32")
    return FileHeader(permissions, properties, alp_command_file_id, interface_file_id, file_size, allocated_size)

  def __iter__(self):
    for byte in self.permissions:
      yield byte

    for byte in self.properties:
      yield byte

    yield self.alp_command_file_id
    yield self.interface_file_id
    for byte in bytearray(struct.pack(">I", self.file_size)):
      yield byte

    for byte in bytearray(struct.pack(">I", self.allocated_size)):
      yield byte



  def __str__(self):
    return "permissions={}, properties=({}), alp_command_file_id={}, interface_file_id={}, file_size={}, allocated_size={}".format(
      self.permissions, self.properties, self.alp_command_file_id, self.interface_file_id, self.file_size, self.allocated_size
    )