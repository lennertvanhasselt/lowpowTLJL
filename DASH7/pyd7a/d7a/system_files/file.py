from d7a.alp.operands.length import Length


class File:
  def __init__(self, id, length):
    self.id = id
    self.length = Length(value=length)
