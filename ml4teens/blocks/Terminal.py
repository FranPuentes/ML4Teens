from IPython.display import update_display, HTML;

from ..core import Block;

class Terminal(Block):

      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);

      #-------------------------------------------------------------------------
      def __print(self, message, plus_style):
          style =f"border:1px black; padding: 5px; margin: 3px; {plus_style}";
          if   type(message) is str:  display( HTML(f"<div style='width:95%; {style}'>{message}</div>") );
          else:                       display( str(message) );

      #-------------------------------------------------------------------------
      @Block.slot("stdin", {str,list,set,tuple,dict}, required=2)
      def slot_stdin(self, slot, data):
          message=data;
          style="background-color: green; color: white";
          self.__print(message,style);
          self.reset("stdin");

      #-------------------------------------------------------------------------
      @Block.slot("stderr", {str,dict}, required=2)
      def slot_stderr(self, slot, data):
          message=data;
          style="background-color: brown; color: white";
          self.__print(message,style);
          self.reset("stderr");

      #-------------------------------------------------------------------------
      def run(self, **kwarg):
          raise RuntimeError("No tiene sentido invocar el método 'run' de un objeto de clase 'Pantalla'.");
