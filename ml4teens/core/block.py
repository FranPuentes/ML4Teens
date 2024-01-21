import random;
import string;
import time;
import types;

from abc import ABC, abstractmethod;

import secrets;

from .context    import Context
from .signalType import SignalType
from .slotType   import SlotType
from .signals    import Signals
from .slots      import Slots

from ..tools     import debug;

#===============================================================================      
class Parameters:

      class StackedDicts:
            
            def __init__(self):
                self._data=[dict()];
                
            def begin(self, _dict=dict()):
                self._data.append(_dict);
                
            def commit(self):
                if len(self._data) > 1:
                   topdict=self._data.pop();
                   for key in topdict:
                       self._data[-1][key]=topdict[key];
                       
            def rollback(self):
                if len(self._data) > 1:
                   topdict=self._data.pop();
                   del topdict;
                       
            def __getitem__(self, key):
                for d in reversed(self._data):
                    if key in d: return d[key];
                raise KeyError(f"No encuentro '{key}' en el diccionario.");    
      
            def __setitem__(self, key, value):
                self._data[-1][key]=value;
      
            def __delitem__(self, key):
                for d in reversed(self._data):
                    if key in d: del d[key];
                raise KeyError(f"No encuentro '{key}' en el diccionario.");    
                
            def __iter__(self):
                rt={};
                for d in reversed(self._data):
                    rt |= {d.keys()};
                return iter(rt);
                
            def __len__(self):
                rt={};
                for d in reversed(self._data):
                    rt |= {d.keys()};
                return len(rt);
                
            def __contains__(self, key):
                rt={};
                for d in reversed(self._data):
                    rt |= {d.keys()};
                return (key in rt);
                
            def get(self, key, default=None):
                for d in reversed(self._data):
                    if key in d: return d[key];
                return default;
          
      #-------------------------------------------------------------------------
      def __init__(self, block, args):
          super().__setattr__('_block', block  );
          super().__setattr__('_data', Parameters.StackedDicts());
          data=self.__dict__.get('_data',None);
          for key in args:
              data[key]=args[key];
          
      def __setitem__(self, key, value):
          data=self.__dict__.get('_data',None);
          if value is not None: data[key]=value;
          else:                 self.__delitem__(key);

      def __getitem__(self, key):
          data=self.__dict__.get('_data',None);
          return data[key];

      def __delitem__(self, key):
          data=self.__dict__.get('_data',None);
          if key in data: del data[key];
          
      def __iter__(self):
          data=self.__dict__.get('_data',None);
          return iter(data);

      def __len__(self):
          data=self.__dict__.get('_data',None);
          return len(data);

      def __contains__(self, key):
          data=self.__dict__.get('_data',None);
          return (key in data) and (data[key] is not None);
          
      def __getattr__(self, key):
          data=self.__dict__.get('_data',None);
          #if key=="keys":   return data.keys;
          #if key=="items":  return data.items;
          #if key=="values": return data.values;
          #if key=="update": return data.update;
          #if key=="pop":    return data.pop;
          #if key=="clear":  return data.clear;
          return data.get(key,None);

      #def __setattr__(self, key, value):
      #    data=self.__dict__.get('_data',None);
      #    if value is not None: data[key]=value;
      #    else:                 del data[key];

      def get(self, key, default=None):
          data=self.__dict__.get('_data',None);
          return data.get(key,default);
          
      def exists(self, key, types=None):
          data=self.__dict__.get('_data',None);
          return (key in data) and (types is None or any([isinstance(data[key],tp) for tp in types]));
      
      def begin(self, _dict=dict()):
          data=self.__dict__.get('_data',None);
          data.begin(_dict);
      
      def commit(self):
          data=self.__dict__.get('_data',None);
          data.commit();
      
      def rollback(self):
          data=self.__dict__.get('_data',None);
          data.rollback();
      
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
          self._params       =Parameters(block=self, args=kwargs);
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
                    func(self, _slot, data if data is not None else default);
                  except Exception as e:
                    debug.print(f"{cls}:: Excepción: '{e}'", exception=e);
                  finally:
                    self.signal_done(f"{self._fullClassName}::{_slot}");
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
      # TODO comprobar que (self,decl) es un slot      
      """
      
      xx[slot]
      xx[slot:{mods}:¿?]
      xx[slot,{mods}]
      
      
      def __getitem__(self, decl):
      
          def convert_str(v):
              try:
                return int(v);
              except ValueError:
                try:
                  return float(v);
                except ValueError:
                  return v;
          
          def split_mods(mod:str) -> dict:
              if '=' in mod:
                 t=[m.strip() for m in mod.split('=',maxsplit=1)];
                 k=" ".join(t[0].split());
                 v=convert_str(t[1]);
              else:
                 k=" ".join(mod.split());
                 v=True;
              return {k:v};
      
          if isinstance(decl,(slice)):
             start=decl.start; # nombre de signal/slot
             stop =decl.stop;  # modificadores
             step =decl.step;  # no usado, por ahora ...
             
             assert isinstance(start,(str)) and bool(start);
             assert isinstance(stop,(str,tuple,list,dict,type(None)));
             #assert isinstance(step,(int,float,type(None)));
             
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
             
             " ""
             # no usado por ahora
             if step: # ...
                if type(step) is int:
                   if step <0:    step=0   /1000;
                   if step >1000: step=1000/1000;
                if type(step) is float:
                   if step <0.0:  step=0.0;
                   if step >1.0:  step=1.0;
                mods.update({"step time to recall":step});
             " ""   
                             
          else:             
             sname=decl;
             mods=None;
          
          assert bool(sname) and isinstance(sname,(str)), f"{self._fullClassName}:: La señal/slot '{sname}' es incorrecta";
          assert (sname in self.signals) or (sname in self.slots), f"No existe la señal/slot '{sname}' en {self._fullClassName}";
          return Context.Linker(self, sname, mods);
      """
      
      #-------------------------------------------------------------------------
      # TODO comprobar que (self,sname) es un signal
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
             