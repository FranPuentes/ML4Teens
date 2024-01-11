
from .type import Type;

#=============================================================================================
class SignalType(Type):

      def __init__(self, tipo):
          super().__init__(tipo,"signal");

      def __eq__(self, st):
      
          from .slotType import SlotType;
          
          assert isinstance(st, SignalType) or isinstance(st, SlotType);
          
          if type(st._type) is set: # signal, sot
             return any([(self._type is T or isinstance(self._type, T)) for T in st._type]);
             
          else: # signal, signal
             return (self._type is st._type);
