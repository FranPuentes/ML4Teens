
from .type import Type;

#=============================================================================================
class SlotType(Type):

      def __init__(self, des):
          super().__init__(des,"slot");

      def __eq__(self, st):
      
          from .signalType import SignalType;
          
          assert isinstance(st, SignalType) or isinstance(st, SlotType);

          if type(st._type) is set: # slot, slot
             return any([(t1 is t2 or isinstance(t1,t2)) for (t1,t2) in {(a,b) for a in self._type for b in st._type}|{(b,a) for a in self._type for b in st._type}]);
 
          else: # slot, signal
             return any([(st._type is T or isinstance(st._type, T)) for T in self._type]);
 
      def __iter__(self):
          return iter(self._type);
          