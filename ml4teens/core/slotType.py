
from .type import Type;

#=============================================================================================
class SlotType(Type):

      def __init__(self, des):
          super().__init__(des,"slot");

      def __eq__(self, st):
          from .signalType import SignalType;
          assert isinstance(st, SignalType) or isinstance(st, SlotType);
          if type(self._type) is set:
             if type(st._type) is set: return any([i in self._type for i in st._type]);
             else:                     return (st._type in self._list);
          else:
             return (isinstance(st, SignalType) and (st._type is self._type)) or (isinstance(st, SlotType) and (self._type in st._type if type(st._type) is set else (self._type is st._type)));
