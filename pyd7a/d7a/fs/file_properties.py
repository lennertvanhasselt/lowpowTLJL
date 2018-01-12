from enum import Enum

from d7a.support.schema import Validatable, Types


class ActionCondition(Enum):
  LIST = 0
  READ = 1
  WRITE = 2
  WRITE_FLUSH = 3


class StorageClass(Enum):
  TRANSIENT = 0
  VOLATILE = 1
  RESTORABLE = 2
  PERMANENT = 3


class FileProperties(Validatable):
  SCHEMA = [{
    "act_enabled": Types.BOOLEAN(),
    "act_cond": Types.ENUM(ActionCondition),
    "storage_class": Types.ENUM(StorageClass)
  }]

  def __init__(self, act_enabled, act_condition, storage_class):
    self.act_enabled = act_enabled
    self.act_condition = act_condition
    self.storage_class = storage_class

    Validatable.__init__(self)

  @staticmethod
  def parse(s):
    act_enabled = s.read("bool")
    act_condition = ActionCondition(s.read("uint:3"))
    _rfu = s.read("uint:2")
    storage_class = StorageClass(s.read("uint:2"))
    return FileProperties(act_enabled, act_condition, storage_class)

  def __iter__(self):
    byte = 0
    if self.act_enabled: byte += 1 << 7
    byte += self.act_condition.value << 4
    byte += self.storage_class.value
    yield byte

  def __str__(self):
    return "act_enabled={}, act_condition={}, storage_class={}".format(
      self.act_enabled,
      self.act_condition,
      self.storage_class
    )