
from .type import Type;

#=============================================================================================
class SignalType(Type):

      def __init__(self, tipo):
          super().__init__(tipo,"signal");

      def __eq__(self, st):
          from .slotType import SlotType;
          assert isinstance(st, SignalType) or isinstance(st, SlotType);
          return (isinstance(st, SignalType) and (self._type is st._type)) or (isinstance(st, SlotType) and ((self._type in st._type) if type(st._type) is set else (self._type is st._type)));
