
from ..core import Block;

class IfElse(Block):
      """
      Recibe en un slot llamado "event".
      Si cumple una condición, emite True por "true", en caso contrario False por "false".
      También emite True/False por la señal 'bool.
      La condición puede ser una lambda pasada por parámetro ("expression").
      La expresión también puede ser un texto, con un avariable local lamada 'data'.
      """

      #-------------------------------------------------------------------------
      # Constructor
      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);

      #-------------------------------------------------------------------------
      # SLOTS
      #-------------------------------------------------------------------------
      @Block.slot("event",{object})
      def slot_event(self, slot, data:object):

          if self.params.expression is not None:
             if   type(self.params.expression) is str:
                  value=bool(eval(self.params.expression, {}, {"data":data}));
             elif callable(self.params.expression):
                  value=bool(self.params.expression(data));
             else: 
                raise RuntimeError(f"La expresión ha de ser o un string o una función, pero es de tipo '{type(self.params.expression)}'");
          else:
             value=bool(data);
      
          self.signal_bool(value);

          if value: self.signal_true (True);
          else:     self.signal_false(False);

      #-------------------------------------------------------------------------
      # SIGNALS
      #-------------------------------------------------------------------------
      @Block.signal("bool",bool)
      def signal_bool(self, data):
          return data;

      @Block.signal("true",bool)
      def signal_true(self, data):
          return True;

      @Block.signal("false",bool)
      def signal_false(self, data):
          return False;
