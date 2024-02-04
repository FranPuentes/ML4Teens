
from ..core import Block;

class ForEach(Block):
      """
      Recibe en un slot llamado "list", que debe ser una lista o una tupla.
      Emite un elemento (item) de la lista cada vez que se le reclama (next).
      Finalmente, cuando no hay más, emite un 'end'
      """

      #-------------------------------------------------------------------------
      # Constructor
      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          self._queue=[];

      #-------------------------------------------------------------------------
      # SLOTS
      #-------------------------------------------------------------------------
      @Block.slot("list",{list,tuple})
      def slot_list(self, slot, data):
          if data:
             for item in data:
                 self._queue.append(item);
                 
             try:
               item=self._queue.pop(0);
               self.signal_item(item);
               
             except IndexError:
               self.signal_end(True);

      #-------------------------------------------------------------------------
      @Block.slot("next",{object})
      def slot_next(self, slot, data):
          try:
            item=self._queue.pop(0);
            self.signal_item(item);
            
          except IndexError:
            self.signal_end(True);
            
      #-------------------------------------------------------------------------
      # SIGNALS
      #-------------------------------------------------------------------------
      @Block.signal("item", object)
      def signal_item(self, data):
          return data;

      @Block.signal("end", bool)
      def signal_end(self, data):
          return data;
