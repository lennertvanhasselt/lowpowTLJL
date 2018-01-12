from d7a.support.schema import Validatable, Types


class FilePermissions(Validatable):
  SCHEMA = [{
    "encrypted": Types.BOOLEAN(),
    "executable": Types.BOOLEAN(),
    "user_readable": Types.BOOLEAN(),
    "user_writable": Types.BOOLEAN(),
    "user_executable": Types.BOOLEAN(),
    "guest_readable": Types.BOOLEAN(),
    "guest_writable": Types.BOOLEAN(),
    "guest_executable": Types.BOOLEAN()
  }]

  def __init__(self, encrypted=False, executeable=False, user_readable=True, user_writeable=True, user_executeable=True,
               guest_readable= True, guest_writeable=True, guest_executeable=True):
    self.encrypted = encrypted
    self.executable = executeable
    self.user_readable = user_readable
    self.user_writeable = user_writeable
    self.user_executeable = user_executeable
    self.guest_readable = guest_readable
    self.guest_writeable = guest_writeable
    self.guest_executeable = guest_executeable

    Validatable.__init__(self)

  @staticmethod
  def parse(s):
    encrypted = s.read("bool")
    executeable = s.read("bool")
    user_readable = s.read("bool")
    user_writeable = s.read("bool")
    user_executable = s.read("bool")
    guest_readable = s.read("bool")
    guest_writeable = s.read("bool")
    guest_executable = s.read("bool")
    return FilePermissions(encrypted=encrypted, executeable=executeable, user_readable=user_readable,
                      user_writeable=user_writeable, user_executeable=user_executable,
                      guest_readable=guest_readable, guest_writeable=guest_writeable, guest_executeable=guest_executable)

  def __iter__(self):
    byte = 0
    if self.encrypted: byte += 1 << 7
    if self.executable: byte += 1 << 6
    if self.user_readable: byte += 1 << 5
    if self.user_writeable: byte += 1 << 4
    if self.user_executeable: byte += 1 << 3
    if self.guest_readable: byte += 1 << 2
    if self.guest_writeable: byte += 1 << 1
    if self.guest_executeable: byte += 1
    yield byte

  def __str__(self):
    return "" #TODO