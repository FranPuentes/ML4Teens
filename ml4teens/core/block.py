import random;
import string;
import threading;
import time;
import queue;

from abc import ABC, abstractmethod;

from .context    import Context
from .signalType import SignalType
from .slotType   import SlotType
from .signals    import Signals
from .slots      import Slots

from ..tools     import debug;

#===============================================================================      
class Parameters:
      
      def __init__(self, block, args):
          super().__setattr__('_block', block );
          super().__setattr__('_data',  dict());                
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
          if key=="keys":   return data.keys;
          if key=="items":  return data.items;
          if key=="values": return data.values;
          if key=="update": return data.update;
          if key=="pop":    return data.pop;
          if key=="clear":  return data.clear;
          return data.get(key,None);

      def __setattr__(self, key, value):
          data=self.__dict__.get('_data',None);
          if value is not None: data[key]=value;
          else:                 del data[key];

      def get(self, key, default=None):
          data=self.__dict__.get('_data',None);
          return data.get(key,default);
          
      def exists(self, key, types=None):
          data=self.__dict__.get('_data',None);
          return (key in data) and (types is None or any([isinstance(data[key],tp) for tp in types]));
      
#===============================================================================
class Tokens:
      
      #-------------------------------------------------------------------------
      class Wrapper:
            def __init__(self, adict):
                super().__setattr__('_dict', adict);
                
            def __setitem__(self, key, value):
                data=self.__dict__.get('_dict',None);
                return data.__setitem__(key,value);
      
            def __getitem__(self, key):
                data=self.__dict__.get('_dict',None);
                return data.__getitem__(key);
      
            def __delitem__(self, key):
                data=self.__dict__.get('_dict',None);
                return data.__delitem__(key);
      
            def __iter__(self):
                data=self.__dict__.get('_dict',None);
                return data.__iter__();
      
            def __len__(self):
                data=self.__dict__.get('_dict',None);
                return data.__len__();
      
            def __contains__(self, key):
                data=self.__dict__.get('_dict',None);
                return data.__contains__(key);

            def __getattr__(self, key):
                data=self.__dict__.get('_dict',None);
                if key=="keys":   return data.keys;
                if key=="items":  return data.items;
                if key=="values": return data.values;
                if key=="update": return data.update;
                if key=="pop":    return data.pop;
                if key=="clear":  return data.clear;
                return data.get(key,None);

            def __setattr__(self, key, value):
                data=self.__dict__.get('_dict',None);
                if value is not None: data[key]=value;
                else:
                   if key=="data": data.__setitem__(key,None);
                   else:           data.__delitem__(key     );

            def get(self, key, default=None):
                data=self.__dict__.get('_dict',None);
                return data.get(key,default);
      
      #-------------------------------------------------------------------------
      def __init__(self, block):
          self._block=block ;
          self._data =dict();
          for sname in self._block.slots:
              self._data[sname]={"data":None};
          
      #-------------------------------------------------------------------------
      def __setitem__(self, sname, token):
          assert sname in self._block.slots, f"{self._block._fullClassName}:: no existe el slot '{sname}'";
          assert type(token) is dict, f"{self._block._fullClassName}:: los tokens debe ser diccionarios";
          assert "data" in token, f"{self._block._fullClassName}:: cada token debe tener al menos una clave 'data'";
          self._data[sname]=token;

      #-------------------------------------------------------------------------
      def __getitem__(self, sname):
          assert sname in self._block.slots, f"{self._block._fullClassName}:: no existe el slot '{sname}'";
          return Tokens.Wrapper(self._data[sname]);

      #-------------------------------------------------------------------------
      def __delitem__(self, sname):
          assert sname in self._block.slots, f"{self._block._fullClassName}:: no existe el slot '{sname}'";
          self._data[sname]={"data":None};
          
      #-------------------------------------------------------------------------
      def __iter__(self):
          return iter(self._data);

      #-------------------------------------------------------------------------
      def __len__(self):
          return len(self._data);

      #-------------------------------------------------------------------------
      def __contains__(self, sname):
          return (sname in self._data);
          
      #-------------------------------------------------------------------------
      def reset(self, sname=None):
          if sname is None:
             for key in self._data:
                 self._data.__setitem__(key,{"data":None});
          else:
             self._data.__setitem__(sname,{"data":None});
          
#===============================================================================      
class Block(ABC):
      """
      La clase Block, ancestro de todos los bloques y núcleo fundamental del sistema, junto con la clase Context.
      """
      
      _boringTimeToFinish=0;
      """
      Si el thread de un objeto de esta clase lleva '_boringTimeToFinish' segundos sin recibir mensajes, finaliza el thread.
      Si es cero, esta funcionalidad se deshabilita.
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
          self._params       =Parameters(block=self, args=kwargs);
          self._tokens       =Tokens(block=self);
          self._queue        =queue.PriorityQueue();
          self._loopFinish   =True;
          self._loopThread   =None;
          self._transitMods  ={};
          self._requestSync  =None; # None => me da igual
          self._lastEventTime=time.time();
          self._id="ID"+''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16));

          if self._fullClassName not in Block._signals: Block._signals[self._fullClassName]=Signals();
          if self._fullClassName not in Block._slots:   Block._slots  [self._fullClassName]=Slots  ();

      #-------------------------------------------------------------------------
      def __hash__(self):
          return hash(self._id);

      #-------------------------------------------------------------------------
      @property
      def params(self):
          return self._params;

      #-------------------------------------------------------------------------
      @property
      def sync(self):
          return self._requestSync;

      @sync.setter
      def sync(self, value):
          if   value is None: self._requestSync=None ;
          elif bool(value):   self._requestSync=True ;
          else:               self._requestSync=False;

      #-------------------------------------------------------------------------
      @property
      def tokens(self):
          return self._tokens;
          
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
                    debug.print(f"Ejecutando {self._fullClassName}::slot('{_slot}',{type(data).__name__}) con mods='{self._transitMods}'", flush=True);
                    func(self, _slot, data);
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
              def wrapper(self, data=None):
                  using=self.checkSignalUsage(name);
                  if data is None:
                     return using;
                  else:
                     if using:
                        data=func(self,data);
                        Context.instance.emit(source=self, sname=name, data=data, mods=self._transitMods);
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
      def reset(self, *args):
          if len(args)==0:
             self.tokens.reset();
          else:
             for k in args:
                 self.tokens.reset(k);

      #-------------------------------------------------------------------------
      """
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
      
      def __call__(self, sname, *args, **kwargs):
          mods={};
          
          for arg in args:
              if type(arg) is str: mods[arg]=True;
              else:                raise RuntimeError(f"El modificador '{arg}' de '{self._fullClassName}:{sname}', debe ser un string.");   
              
          for key in kwargs:
              mods[key]=kwargs[key];
              
          return Context.Linker(self, sname, mods);
      
      #-------------------------------------------------------------------------
      def terminate(self):
          if self._loopThread and self._loopThread.is_alive():
             self._loopFinish=True;
             self._loopThread.join();
             self._loopThread=None;
             
          while not self._queue.empty(): self._queue.get();
          
          self._loopFinish=True;
          self._loopThread=None;
        
          self.reset();
                    
      #-------------------------------------------------------------------------
      def boredTime(self):
          """
          Tiempo, en segundos, transcurrido desde el último evento recibido.
          """
          return (time.time()-self._lastEventTime);
          
      #-------------------------------------------------------------------------
      def running(self):
          return (self._loopThread is not None and self._loopThread.is_alive());
          
      #-------------------------------------------------------------------------
      def run_sync(self, tm, sname, token, mods:dict):
      
          cls=self._fullClassName;
          
          self.tokens[sname]=token;
          
          debug.print(f"{cls}:: nuevo evento '{sname}' con data={type(self.tokens[sname].data)}, con mods={mods}");
          
          if sname in self.slots:
          
             slot=self.slots[sname];
             
             data=self.tokens[sname].data or slot["default"];
             
             assert any([isinstance(data,tp) for tp in slot["type"]]), f"El slot '{sname}' de {self._fullClassName} no acepta datos de tipo '{type(data)}', sólo estos tipos: {slot['type']}";
             
             try:
               self._transitMods=mods;
               func=slot["stub"];
               func(self,sname,data);
               
             finally:
               mod_keep =mods.get("keep" ) if mods is not None else False;
               mod_clean=mods.get("clean") if mods is not None else False;                           
               if bool(mod_clean): del self.tokens[sname];
               if bool(mod_keep ): self.tokens[sname]=token;
               self._transitMods={};
               
          else:
             raise RuntimeError(f"{cls}:: '{sname}' no existe como slot");
                    
          
      #-------------------------------------------------------------------------
      def run(self):
      
          def _loop():
          
              # si esta clase no tiene slots, no tiene sentido entrar en el bucle.
              cls=self._fullClassName;
              if cls not in Block._slots:
                 self._loopFinish=True;
                 return;
                 
              debug.print(f"Iniciando un THREAD ({cls})");
              self._loopFinish=False;
              self._lastEventTime=time.time();
              while not self._loopFinish:
                    try:
                      tm, sname, token, mods = self._queue.get(block=True, timeout=1);
                      
                      self.run_sync(tm, sname, token, mods);
                      
                    except queue.Empty:
                      debug.print(f"{cls}:: Llevo aburriéndome {int(self.boredTime())} segundos");
                      if Block._boringTimeToFinish>0 and self.boredTime()>Block._boringTimeToFinish and self._queue.empty():
                         break;
                    
                    except Exception as e:
                      debug.print(f"{cls}:: se ha producido una excepción: {str(e)}", exception=e);
                      
              while not self._queue.empty(): self._queue.get();
              debug.print(f"{cls}:: THREAD finalizado");
              self._loopFinish=True;
              #-------------
          
          if self._loopThread is None or not self._loopThread.is_alive():
             self._loopThread=threading.Thread(target=_loop);
             self._loopThread.start();
          else:
             self._lastEventTime=time.time();

if __name__=="__main__":
   
   params=Parameters(block=None, args={"1":1, "2":2, "3":3});
   
   