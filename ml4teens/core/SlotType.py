#=============================================================================================
class SlotType(Type):

      def __init__(self, des):
          super().__init__(des,"slot");

      def match(self, st):
          assert isinstance(st, SignalType), "El método 'match' de SlotType debe recibir una instancia de SignalType como parámetro";
          if type(self._type) is set: return any([(st._type is t) for t in self._type]);
          else:                       return (st._type is self._type);

      def __eq__(self, st):
          assert isinstance(st, SignalType) or isinstance(st, SlotType);
          if type(self._type) is set:
             if type(st._type) is set: return any([i in self._type for i in st._type]);
             else:                     return (st._type in self._list);
          else:
             return (isinstance(st, SignalType) and (st._type is self._type)) or (isinstance(st, SlotType) and (self._type in st._type if type(st._type) is set else (self._type is st._type)));
