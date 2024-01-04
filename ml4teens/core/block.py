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
      
class Block(ABC):

      _boringTimeToFinish=2;

      _signals={};
      _slots  ={};

      #-------------------------------------------------------------------------
      @staticmethod
      def _classNameFrom(func):
          assert hasattr(func, '__module__') and  hasattr(func, '__qualname__') and ('.' in func.__qualname__);
          return f"{func.__module__}::{func.__qualname__.split('.', maxsplit=1)[0]}";

      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          self._params       ={};
          self._values       ={};
          self._queue        =queue.PriorityQueue();
          self._loopFinish   =True;
          self._loopThread   =None;
          self._lastEventTime=time.time();
          self._fullClassName=Block._classNameFrom(self.__init__);
          self._id="ID"+''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16));
          for key in kwargs: self._params[key]=kwargs[key];

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
                        if data is not None:
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
                    self._values[k]=None;

      #-------------------------------------------------------------------------
      def __hash__(self):
          return hash(self._id);

      #-------------------------------------------------------------------------
      def __getitem__(self, a_name):
          assert (a_name in self.signals) or (a_name in self.slots), f"No existe la señal/slot '{a_name}' en {self._fullClassName}";
          return Context.Linker(self, a_name);

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
                      _, sname, data = self._queue.get(block=True, timeout=1);
                      self._lastEventTime=time.time();
                      debug.print(f"{cls}:: nuevo evento '{sname},{type(data)}'");
                      if sname in Block._slots[cls]:
                         slot=Block._slots[cls][sname];
                         data=data if data is not None else slot["default"];
                         self._values[sname]=data;
                         group=slot["required"];
                         complete_slots=self.slots.iscomplete(self._values);
                         assert group in complete_slots;
                         if bool(complete_slots) and (sname in complete_slots[group]):
                            try:
                              func=slot["stub"];
                              func(self,sname,data);
                            except Exception as e:
                              debug.print(f"{cls}:: excepción en el slot '{sname}': {str(e)}");
                              #traceback.print_exc(file=sys.stdout);
                      else:
                         debug.print(f"{cls}:: '{sname}' no existe como slot");
                    
                    except queue.Empty:
                      debug.print(f"{cls}:: Llevo aburriéndome {int(self.boredTime())} segundos");
                      if self.boredTime()>Block._boringTimeToFinish:
                         break;
                    
                    except Exception as e:
                      debug.print(f"{cls}:: se ha producido una excepción: {str(e)}");
                      #traceback.print_exc(file=sys.stdout);
                      
              while not self._queue.empty(): self._queue.get();
              debug.print(f"{cls}:: THREAD finalizado");
              self._loopFinish=True;
              #-------------
          
          if self._loopThread is None or not self._loopThread.is_alive():
             self._loopThread=threading.Thread(target=_loop);
             self._loopThread.start();
          