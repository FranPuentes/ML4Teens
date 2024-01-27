import random;
import string;
import time;
import types;

from abc import ABC, abstractmethod;

import secrets;

from jupyter_ui_poll import ui_events;

from .context    import Context
from .signalType import SignalType
from .slotType   import SlotType
from .signals    import Signals
from .slots      import Slots

from ..tools     import debug;

#===============================================================================      
class StackedDicts:
      
      def __all__(self):
          rt=dict();
          for d in self._data: rt.update(d);
          return rt;
      
      #···································································    
      def __init__(self, **kwargs):
          self._data=[dict(**kwargs)];
          
      #···································································    
      def begin(self, _dict=dict()):
          self._data.append(_dict);
          
      #···································································    
      def commit(self):
          if len(self._data) > 1:
             rt=self._data.pop();
             for key in rt:
                 self._data[-1][key]=rt[key];
                 
      #···································································    
      def rollback(self):
          if len(self._data) > 1:
             rt=self._data.pop();
             del rt;
                 
      #···································································    
      def __getitem__(self, key):
          for d in reversed(self._data):
              if key in d: return d[key];
          return None; # cuidado! rompe el estándar.

      #···································································    
      def __setitem__(self, key, value):
          self._data[-1][key]=value;

      #···································································    
      def __delitem__(self, key):
          self._data[-1][key]=None; # cuidado! rompe el estándar.
          
      #···································································    
      def __iter__(self):
          rt=self.__all__();
          return iter(rt);
          
      #···································································    
      def __len__(self):
          rt=self.__all__();
          return len(rt);
          
      #···································································    
      def __contains__(self, key):
          rt=self.__all__();
          return (key in rt);
          
      #···································································    
      def __str__(self):
          return str(self.__all__());

      #···································································    
      def __repr__(self):
          return (self.__all__()).__repr__();

      #···································································    
      def get(self, key, default=None):
          rt=self.__all__();
          return rt.get(key,default);
    
      #···································································    
      def keys(self):
          rt=self.__all__();
          return rt.keys();
          
      #···································································    
      def items(self):
          rt=self.__all__();
          return rt.items();
          
      #···································································    
      def values(self):
          rt=self.__all__();
          return rt.values();
          
      #···································································    
      def update(self, *args, **kwargs):
          return self._data[-1].update(*args, **kwargs);
          
      #···································································    
      def pop(self, *args, **kwargs):
          return self._data[-1].pop(*args, **kwargs);

      #-------------------------------------------------------------------------
      def __getattr__(self, name):
          return self.__getitem__(name);

#===============================================================================      
class Block(ABC):
      """
      La clase Block, ancestro de todos los bloques y núcleo fundamental del sistema, junto con la clase Context.
      """
      
      _signals={};
      _slots  ={};

      #-------------------------------------------------------------------------
      @staticmethod
      def _classNameFrom(func):
          assert hasattr(func, '__module__') and  hasattr(func, '__qualname__') and ('.' in func.__qualname__);
          return f"{func.__module__}:{func.__qualname__.split('.', maxsplit=1)[0]}";

      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          self._fullClassName=Block._classNameFrom(self.__init__);
          self._signal_mods  ={};
          self._params       =StackedDicts(**kwargs);
          self._id="ID"+''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16));

          cls=self._fullClassName;
          
          if self._fullClassName not in Block._signals: Block._signals[cls]=Signals();
          if self._fullClassName not in Block._slots:   Block._slots  [cls]=Slots  ();
          
          Block._signals[cls]["done"]=SignalType(str);
          _unique_ = secrets.token_hex(32);
          def wrapper(self, data=_unique_):
              using=self.checkSignalUsage("done");
              if data is _unique_:
                 return using;
              else:
                 if using:
                    Context.instance.emit(source=self, sname="done", data=data, mods=self._signal_mods);
          self.signal_done=types.MethodType(wrapper, self);
          
      #-------------------------------------------------------------------------
      def __hash__(self):
          return hash(self._id);

      #-------------------------------------------------------------------------
      @property
      def params(self):
          return self._params;

      #-------------------------------------------------------------------------
      @property
      def signals(self):
          return Block._signals[self._fullClassName];

      #-------------------------------------------------------------------------
      @property
      def slots(self):
          return Block._slots[self._fullClassName];

      #-------------------------------------------------------------------------
      @staticmethod
      def slot(name, typedecl, default=None):
          def decorador(func):
              cls=Block._classNameFrom(func);
              if cls not in Block._slots:   Block._slots  [cls]=Slots  ();
              if cls not in Block._signals: Block._signals[cls]=Signals();
              Block._slots[cls][name]={ "type":SlotType(typedecl), "required":0, "default":default };
              Block._slots[cls][name]["name"]=name;
              Block._slots[cls][name]["stub"]=func;
              def wrapper(self, _slot, data):
                  try:
                    assert name == _slot;
                    debug.print(f"Ejecutando {self._fullClassName}::slot('{_slot}',{type(data).__name__})'");
                    assert func is not None;
                    assert callable(func);
                    
                    done=func(self, _slot, data);
                    
                    if self.params.done is not None:
                       if callable(self.params.done):
                          done=self.params.done(data);
                          self.signal_done(done);
                       else:
                          done=self.params.done;
                          self.signal_done(done);
                    else:
                       if bool(done) is True: # SUGGEST: enviar el valor de 'done' si no es None.
                          self.signal_done(f"{self._fullClassName}::{_slot}");
                       
                  except Exception as e:
                    debug.print(f"{cls}:: Excepción: '{e}'", exception=e);
                    
                  finally:
                    pass;
                    
              Block._slots[cls][name]["stub"]=wrapper;
              return wrapper;
          return decorador;

      #-------------------------------------------------------------------------
      @staticmethod
      def signal(name, typedecl):
          def decorador(func):
              cls=Block._classNameFrom(func);
              if cls not in Block._slots:   Block._slots  [cls]=Slots  ();
              if cls not in Block._signals: Block._signals[cls]=Signals();
              Block._signals[cls][name]=SignalType(typedecl);
              _unique_ = secrets.token_hex(32);
              def wrapper(self, data=_unique_):
                  using=self.checkSignalUsage(name);
                  if data is _unique_:
                     return using;
                  else:
                     if using:
                        data=func(self,data);
                        Context.instance.emit(source=self, sname=name, data=data, mods=self._signal_mods);
              return wrapper;
          return decorador;

      #-------------------------------------------------------------------------
      def checkSignalUsage(self, name):
          """
          Comprueba si el evento (*signal*) está asociado a un *slot*.
          Es equivalente a invocar el método (decorado) correspondente al evento, pero con *data=None*.          
          
          :param name: Nombre del evento (*signal*)
          :type  name: str
          :return:     True si la señal está asocida a un *slot*, False en caso contrario.
          :rtype:      bool
          """
          context=Context.instance;
          return context.checkSubscription((self,name));

      #-------------------------------------------------------------------------
      @staticmethod
      def waitUntil(finish):
          assert callable(finish);
          with ui_events() as poll:
               while not finish():
                     poll(10);
                     time.sleep(0.1);
      
      #-------------------------------------------------------------------------
      def __getitem__(self, decl):
          
          #·····································································
          def convert_str(v):
              try:
                return int(v);
              except ValueError:
                try:
                  return float(v);
                except ValueError:
                  if v.lower()=="null":  return None;
                  if v.lower()=="none":  return None;
                  if v.lower()=="true":  return True;
                  if v.lower()=="false": return False;
                  return v;
          
          #·····································································
          def split_mods(mods:str) -> dict:
              rt=dict();
              for mod in [m.strip() for m in mods.split(',')]:
                  if '=' in mod:
                     t=[m.strip() for m in mod.split('=',maxsplit=1)];
                     k=" ".join(t[0].split());
                     v=convert_str(t[1]);
                  else:
                     k=" ".join(mod.split());
                     v=True;
                  rt.update({k:v});
              return rt;
              
          #·····································································
          assert isinstance(decl,(str,slice));
      
          if isinstance(decl,(slice)):
             start=decl.start; # nombre del slot
             stop =decl.stop;  # modificadores
             step =decl.step;
             
             assert isinstance(start,(str)) and bool(start);
             assert isinstance(stop,(str,tuple,list,dict,type(None)));
             
             sname=start;
             
             mods={};
             
             if stop: # modificadores del signal/slot
             
                if   type(stop) is str:
                     v=split_mods(stop);
                     mods.update(v);
                     
                elif isinstance(stop,(tuple,list)):
                     for m in stop:
                         assert type(m) is str;
                         v=split_mods(m);
                         mods.update(v);
                         
                elif isinstance(stop,dict):
                     mods.update(stop);
                     
          else:
             sname=decl;
             mods=None;
          
          assert bool(sname) and isinstance(sname,(str,)), f"{self._fullClassName}:: La señal/slot '{sname}' es incorrecta";
          assert sname in self.slots, f"No existe el slot '{sname}' en {self._fullClassName}";
          return Context.Linker(self, sname, mods);
      
      #-------------------------------------------------------------------------
      def __call__(self, sname, *args, **kwargs):
          mods={};
          
          for arg in args:
              if type(arg) is str: mods[arg]=True;
              else:                raise RuntimeError(f"El modificador '{arg}' de '{self._fullClassName}:{sname}', debe ser un string.");   
              
          for key in kwargs:
              mods[key]=kwargs[key];
              
          return Context.Linker(self, sname, mods);
      
      #-------------------------------------------------------------------------
      def run(self, sname, data, mods):
      
          cls=self._fullClassName;
          
          debug.print(f"{cls}:: nuevo evento '{sname}' con data={type(data)}");
          
          if sname in self.slots:
          
             slot=self.slots[sname];
             
             # TODO: ¿realmente necesitamos un valor por defecto?
             #data=data if data is not None else slot["default"];
             
             assert data is None or any([isinstance(data,tp) for tp in slot["type"]]), f"El slot '{sname}' de {self._fullClassName} no acepta datos de tipo '{type(data)}', sólo estos tipos: {slot['type']} o None";
             
             assert type(mods) in (tuple,list) and len(mods)==2 and all([(type(m) is dict) for m in mods]);
             
             signal_mods, slot_mods = mods;
             
             try:
               self._signal_mods=signal_mods;
               self.params.begin(signal_mods|slot_mods);
               func=slot["stub"];
               assert callable(func);
               func(self,sname,data);               
             finally:
               self._signal_mods={};
               self.params.rollback();
               
          else:
             raise RuntimeError(f"{cls}:: '{sname}' no existe como slot");


             