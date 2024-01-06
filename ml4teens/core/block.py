import sys, traceback;

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

#TODO considerar hacer una clase Params para manejar los parámetros (incluso con pop, push).
      
#TODO considerar hacer una clase Values para manejar los valores de los slots.

#TODO considerar que Block no herede de ABC, ya no lo necesita.
      
class Block(ABC):
      """
      La clase Block, ancestro de todos los bloques y núcleo fundamental del sistema, junto con la clase Context.
      """
      
      _boringTimeToFinish=0;
      """ Si el thread de un objeto de esta clase lleva '_boringTimeToFinish' segundos sin recibir mensajes, finaliza el thread.
          Si es cero, esta funcionalidad se deshabilita. """

      _signals={};
      _slots  ={};

      #-------------------------------------------------------------------------
      @staticmethod
      def _classNameFrom(func):
          assert hasattr(func, '__module__') and  hasattr(func, '__qualname__') and ('.' in func.__qualname__);
          return f"{func.__module__}:{func.__qualname__.split('.', maxsplit=1)[0]}";

      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          self._params       ={};
          self._values       ={};
          self._counter      ={};
          self._queue        =queue.PriorityQueue();
          self._loopFinish   =True;
          self._loopThread   =None;
          self._lastEventTime=time.time();
          self._fullClassName=Block._classNameFrom(self.__init__);
          self._id="ID"+''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16));

          for key in kwargs:
              self._params[key]=kwargs[key];

          for sname in self.slots:
              self._values [sname]=None;
              self._counter[sname]=0;

      #-------------------------------------------------------------------------
      def _param(self, key, default=None):
          return self._params.get(key, default);

      #-------------------------------------------------------------------------
      def _value(self, key, default=None):
          return self._values.get(key, default);
          
      #-------------------------------------------------------------------------
      def getValue(self, key):
          rt=self._values.get(key);
          if rt is None: rt=self.slots[key]["default"];
          return rt;
          
      #-------------------------------------------------------------------------
      def setValue(self, key, value):
          self._values[key]=value;
      
      #-------------------------------------------------------------------------
      def rightValue(self, key):
          return self.getValue(key) is not None;

      #-------------------------------------------------------------------------
      @property
      def signals(self):
          return Block._signals.get(self._fullClassName,dict());

      #-------------------------------------------------------------------------
      @property
      def slots(self):
          return Block._slots.get(self._fullClassName,dict());

      #-------------------------------------------------------------------------
      @staticmethod
      def slot(name, typedecl, required, default=None):
          def decorador(func):
              cls=Block._classNameFrom(func);
              if cls not in Block._slots:   Block._slots  [cls]=Slots  ();
              if cls not in Block._signals: Block._signals[cls]=Signals();
              Block._slots[cls][name]={ "type":SlotType(typedecl), "required":required, "default":default };
              Block._slots[cls][name]["name"]=name;
              Block._slots[cls][name]["stub"]=func;
              def wrapper(self, _slot):
                  data = self._value(name,Block._slots[cls][name]["default"]);
                  func(self, _slot, data);
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
                  if data is None:
                     return self.checkSignalUsage(name);
                  else:
                     if self.checkSignalUsage(name):
                        data=func(self,data);
                        #if data is not None:
                        Context.instance.emit(source=self, sname=name, data=data);
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
             self._values={};
          else:
             for k in args:
                 if k in self._values:
                    self._values [k]=None;
                    self._counter[k]=0;

      #-------------------------------------------------------------------------
      def __hash__(self):
          return hash(self._id);

      #-------------------------------------------------------------------------
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
             start=decl.start;
             stop =decl.stop;
             step =decl.step;
             
             assert isinstance(start,(str)) and bool(start);
             assert isinstance(stop,(str,tuple,list,type(None)));
             assert isinstance(step,(int,float,type(None)));
             
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
             
             if step: # milisegundos para volver a intentar un evento
                if type(step) is int:
                   if step <0:    step=0   /1000;
                   if step >1000: step=1000/1000;
                if type(step) is float:
                   if step <0.0:  step=0.0;
                   if step >1.0:  step=1.0;
                mods.update({"step time to recall":step});
                             
          else:
             sname=decl;
             mods=None;
          
          assert bool(sname) and isinstance(sname,(str)), f"{self._fullClassName}:: La señal/slot '{sname}' es incorrecta";
          assert (sname in self.signals) or (sname in self.slots), f"No existe la señal/slot '{sname}' en {self._fullClassName}";
          return Context.Linker(self, sname, mods);

      #-------------------------------------------------------------------------
      def terminate(self, clear_all=True):
          if self._loopThread and self._loopThread.is_alive():
             self._loopFinish=True;
             self._loopThread.join();
             self._loopThread=None;
             
          self._loopFinish=True;
          self._loopThread=None;
          
          if clear_all:
             self._values ={};
             while not self._queue.empty(): self._queue.get();
          
      #-------------------------------------------------------------------------
      def boredTime(self):
          return (time.time()-self._lastEventTime);
          
      #-------------------------------------------------------------------------
      def running(self):
          return not (self._loopThread is None or not self._loopThread.is_alive());
          
      #-------------------------------------------------------------------------
      def run(self):
      
          def _loop():
          
              cls=self._fullClassName;
              if cls not in Block._slots:
                 self._loopFinish=True;
                 return;
                 
              debug.print(f"Iniciando un THREAD ({cls})");
              self._loopFinish=False;
              self._lastEventTime=time.time();
              while not self._loopFinish:
                    try:
                      tm, sname, data, times, mods = self._queue.get(block=True, timeout=1);
                      
                      debug.print(f"{cls}:: nuevo evento '{sname},{type(data)}' con mods={mods}, y times={times}", flush=True);
                      
                      if sname in self.slots:
                      
                         slot=self.slots[sname];
                         
                         data=data if data is not None else slot["default"];

                         try:
                           func=slot["stub"];
                           if data:
                              func(self,sname,data);
                              
                         except Exception as e:
                           debug.print(f"{cls}:: excepción en el slot '{sname}': {str(e)}");
                           traceback.print_exc(file=sys.stdout);
                           
                         finally:
                           self._counter[sname] += 1;
                           
                           mod_keep =mods.get("keep" ) if mods is not None else False;
                           mod_clean=mods.get("clean") if mods is not None else False;
                           
                           if bool(mod_clean): self._values[sname]=None;
                           if bool(mod_keep ): self._values[sname]=data;
                           
                      else:
                         raise RuntimeError(f"{cls}:: '{sname}' no existe como slot");
                    
                    except queue.Empty:
                      debug.print(f"{cls}:: Llevo aburriéndome {int(self.boredTime())} segundos");
                      if Block._boringTimeToFinish>0 and self.boredTime()>Block._boringTimeToFinish and self._queue.empty():
                         break;
                    
                    except Exception as e:
                      debug.print(f"{cls}:: se ha producido una excepción: {str(e)}");
                      traceback.print_exc(file=sys.stdout);
                      
              while not self._queue.empty(): self._queue.get();
              debug.print(f"{cls}:: THREAD finalizado");
              self._loopFinish=True;
              #-------------
          
          if self._loopThread is None or not self._loopThread.is_alive():
             self._loopThread=threading.Thread(target=_loop);
             self._loopThread.start();
          else:   
             self._lastEventTime=time.time();
          