from IPython.display import update_display, HTML;
import json;

from ..core import Block;

class Terminal(Block):

      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);

      #-------------------------------------------------------------------------
      def __print(self, message, plus_style):
          style =f"border:1px black; padding: 5px; margin: 3px; {plus_style}";
          if   type(message) is str:   display( HTML(f"<div style='width:95%; {style}'>{    message }</div>") );
          elif type(message) is dict:  display( HTML(f"<div style='width:95%; {style}'>{str(message)}</div>") );
          else:
             obj=message;
             message=json.dumps(obj, indent=2, skipkeys=True);
             display( HTML(f"<div style='width:95%; {style}'><pre>{message}</pre></div>") );

      #-------------------------------------------------------------------------
      @Block.slot("stdout", {str,list,set,tuple,dict,object})
      def slot_stdin(self, slot, data):
          message=data;
          style="background-color: green; color: white";
          self.__print(message,style);

      #-------------------------------------------------------------------------
      @Block.slot("stderr", {str,list,set,tuple,dict,object})
      def slot_stderr(self, slot, data):
          message=data;
          style="background-color: brown; color: white";
          self.__print(message,style);

