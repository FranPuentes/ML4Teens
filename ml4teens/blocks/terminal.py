import io;
import pprint;
import json;
import html;

from IPython.display import update_display, HTML;

from ..core import Block;

def escape(t):
    return (t.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace("'", "&#39;")
             .replace('"', "&quot;")
           );


class Terminal(Block):

      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          self._outstyle="background-color: #dcffdb; color: black";
          self._errstyle="background-color: #ffe7cf; color: black";

      #-------------------------------------------------------------------------
      def __print(self, message, plus_style):
          style =f"border:1px black; padding: 5px; margin: 3px; {plus_style}";
          if isinstance(message, (bool,int,float,str)):
             pass;
          else:
             buffer = io.StringIO();
             pp = pprint.PrettyPrinter(stream=buffer);
             pp.pprint(message);
             message = buffer.getvalue();
          
          message=escape(str(message));
          display( HTML(f"<pre style='{style}'>{message}</pre>") );

      #-------------------------------------------------------------------------
      @Block.slot("stdout", {str,list,set,tuple,dict,object})
      def slot_stdin(self, slot, data):
          message=data if not(data is None or (type(data)==str and data=='')) else self.params.message;
          self.__print(message,self._outstyle);
          if self.params.dump:
             style="background-color: blue; color: white";
             self.__print(self.params,style);

      #-------------------------------------------------------------------------
      @Block.slot("stderr", {str,list,set,tuple,dict,object})
      def slot_stderr(self, slot, data):
          message=data if not(data is None or data=='') else self.params.message;
          self.__print(message,self._errstyle);
          if self.params.dump:
             style="background-color: blue; color: white";
             self.__print(self.params,style);

