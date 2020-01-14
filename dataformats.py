import enum


@enum.unique
class Commands(enum.Enum):
  wakeword = enum.auto()
  startclip = enum.auto()
  endclip = enum.auto()
  placemarker = enum.auto()
