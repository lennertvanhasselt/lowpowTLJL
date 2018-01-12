from d7a.fs.file_header import FileHeader
from d7a.support.schema import Validatable, Types


class FileHeaderOperand(Validatable):

  SCHEMA = [{
    "file_id": Types.BYTE(),
    "file_header": Types.OBJECT(FileHeader)
  }]

  def __init__(self, file_id, file_header):
    self.file_id = file_id
    self.file_header = file_header
    super(FileHeaderOperand, self).__init__()

  def __iter__(self):
    yield self.file_id
    for byte in self.file_header: yield byte

  @staticmethod
  def parse(s):
    file_id = s.read("uint:8")
    file_header = FileHeader.parse(s)
    return FileHeaderOperand(file_id=file_id, file_header=file_header)

  def __str__(self):
    return "file-id={}, header={}".format(self.file_id, self.file_header)