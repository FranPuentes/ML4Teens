# -*- coding: utf-8 -*-

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
      """
      Muestra (display) la información que se le envía como texto.
      Es adecuado para visualizar textos, listas, diccionarios, etc.
      
      Tiene dos tipos de slots: stdout y out por un lado, y stderr y error por el otro.
      Ambos grupos se diferencian en los colores que se emplean, nada más.
      Los slots stdout y stderr mustran las información usando <pre>, mientras que out y error usan <p>.
      Esto último se puede cambiar usando los parámetros 'p' y 'pre'.
      """
      
      parameters=[ {"name":"feed",    "type":"bool",   "default":"False",      "doc":"Añade o substituye lo último mostrado"},
                   {"name":"p",       "type":"bool",   "default":"True/False", "doc":"Usa la etiqueta <p>"},
                   {"name":"pre",     "type":"bool",   "default":"True/False", "doc":"Usa la etiqueta <pre>"},
                   {"name":"dump",    "type":"bool",   "default":"False",      "doc":"En stdout/stderr muestra los parámetros recibidos"},
                   {"name":"message", "type":"string", "default":"None",       "doc":"Texto a mostrar si se recibe un texto vacío"},
                 ];

      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          self._outstyle="background-color: #dcffdb; color: black";
          self._errstyle="background-color: #ffe7cf; color: black";

      #-------------------------------------------------------------------------
      def __print(self, message, plus_style, _pre=False, _p=False):
          style =f"border:1px black; padding: 5px; margin: 3px; font-family: monospace; {plus_style}";
          if isinstance(message, (bool,int,float,str)):
             pass;
          else:
             buffer = io.StringIO();
             pp = pprint.PrettyPrinter(stream=buffer, indent=4, width=80, depth=2, compact=False, sort_dicts=True);
             pp.pprint(message);
             message = buffer.getvalue();
             
          """
               for p in message.split('\n'):
                   if p.strip(): 
                      display( HTML(f"<p style='{style}'>{p.strip()}</p>"), display_id=self._id if not self.params.feed else None);
          """   
          
          if   bool(self.params.p or _p):
               message=escape(str(message));
               display( HTML(f"<p style='{style}'>{message}</p>"), display_id=self._id if not self.params.feed else None);
          elif bool(self.params.pre or _pre):
               message=escape(str(message));
               display( HTML(f"<pre style='{style}'>{message}</pre>"), display_id=self._id if not self.params.feed else None);
          else:
               message=escape(str(message));
               display( HTML(f"<div style='{style}'>{message}</div>"), display_id=self._id if not self.params.feed else None );

      #-------------------------------------------------------------------------
      @Block.slot("stdout", {str,list,set,tuple,dict,object})
      def slot_stdout(self, slot, data):
          message=data if not(data is None or (type(data)==str and data=='')) else self.params.message;
          self.__print(message,self._outstyle, _pre=True);
          if self.params.dump:
             style="background-color: blue; color: white";
             self.__print(self.params,style, _pre=True);

      #-------------------------------------------------------------------------
      @Block.slot("out", {str,list,set,tuple,dict,object})
      def slot_out(self, slot, data):
          message=data if not(data is None or (type(data)==str and data=='')) else self.params.message;
          self.__print(message,self._outstyle, _p=True);

      #-------------------------------------------------------------------------
      @Block.slot("stderr", {str,list,set,tuple,dict,object})
      def slot_stderr(self, slot, data):
          message=data if not(data is None or data=='') else self.params.message;
          self.__print(message,self._errstyle, _pre=True);
          if self.params.dump:
             style="background-color: blue; color: white";
             self.__print(self.params,style, _pre=True);

      #-------------------------------------------------------------------------
      @Block.slot("error", {str,list,set,tuple,dict,object})
      def slot_err(self, slot, data):
          message=data if not(data is None or data=='') else self.params.message;
          self.__print(message,self._errstyle, _p=True);
