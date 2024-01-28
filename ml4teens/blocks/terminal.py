import io;
import pprint;
import json;

from IPython.display import update_display, HTML;

from ..core import Block;

class Terminal(Block):

      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          self._outstyle="background-color: #dcffdb; color: black";
          self._errstyle="background-color: #ffe7cf; color: black";

      #-------------------------------------------------------------------------
      def __print(self, message, plus_style):
          style =f"border:1px black; padding: 5px; margin: 3px; {plus_style}";
          #if   type(message) is str:   display( HTML(f"<div style='width:95%; {style}'>str:{    message }</div>") );
          #elif type(message) is dict:  display( HTML(f"<div style='width:95%; {style}'>dict:{str(message)}</div>") );
          #elif type(message) is int:   display( HTML(f"<div style='width:95%; {style}'>int{    message }</div>") );
          #elif type(message) is bool:  display( HTML(f"<div style='width:95%; {style}'>bool{    message }</div>") );
          #else:
          if isinstance(message, (bool,int,float,str)):
             pass;
          else:
             buffer = io.StringIO();
             pp = pprint.PrettyPrinter(stream=buffer);
             pp.pprint(message);
             message = buffer.getvalue();
             
          display( HTML(f"<div style='{style}'>{message}</div>") );

      #-------------------------------------------------------------------------
      @Block.slot("stdout", {str,list,set,tuple,dict,object})
      def slot_stdin(self, slot, data):
          message=data or self.params.message;
          self.__print(message,self._outstyle);
          if self.params.dump:
             style="background-color: blue; color: white";
             self.__print(self.params,style);

      #-------------------------------------------------------------------------
      @Block.slot("stderr", {str,list,set,tuple,dict,object})
      def slot_stderr(self, slot, data):
          message=data or self.params.message;
          self.__print(message,self._errstyle);
          if self.params.dump:
             style="background-color: blue; color: white";
             self.__print(self.params,style);

