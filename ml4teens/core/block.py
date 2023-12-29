import random;
import string;

from abc import ABC, abstractmethod;

from .context    import Context
from .signalType import SignalType
from .slotType   import SlotType
from .signals    import Signals
from .slots      import Slots

class Block(ABC):

      _signals={};
      _slots  ={};

      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          self._params ={};
          self._values ={};
          self._id     ="ID"+''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16));
          for key in kwargs: self._params[key]=kwargs[key];

      #-------------------------------------------------------------------------
      def _param(self, key, default=None):
          if key in self._params: return self._params[key];
          else:                   return default;

      #-------------------------------------------------------------------------
      def _value(self, key, default=None):
          if key in self._values: return self._values[key];
          else:                   return default;

      #-------------------------------------------------------------------------
      @staticmethod
      def _classNameFrom(func):
          assert hasattr(func, '__module__') and  hasattr(func, '__qualname__') and ('.' in func.__qualname__);
          return f"{func.__module__}::{func.__qualname__.split('.', maxsplit=1)[0]}";

      #-------------------------------------------------------------------------
      @property
      def signals(self):
          classname=Block._classNameFrom(self.__init__);
          if classname in Block._signals:
             return Block._signals[classname];
          else:
             return {};

      #-------------------------------------------------------------------------
      @property
      def slots(self):
          classname=Block._classNameFrom(self.__init__);
          if classname in Block._slots:
             return Block._slots[classname];
          else:
             return {};

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
              if cls not in Block._signals: Block._signals[cls]=Signals();
              Block._signals[cls][name]=SignalType(typedecl);
              def wrapper(self, data=None):
                  if data is None:
                     return self.checkSignalUsage(name);
                  else:
                     if self.checkSignalUsage(name):
                        data=func(self,data);
                        if data is not None:
                           Context.instance.emit(self,name,data);
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
          assert (a_name in self.signals) or (a_name in self.slots), f"No existe la señal/slot '{a_name}' en {Block._classNameFrom(self.__init__)}";
          return Context.Linker(self, a_name);

      #-------------------------------------------------------------------------
      @abstractmethod
      def run(self, **kwarg):
          pass;

      #-------------------------------------------------------------------------
      def __call__(self, **kwargs):
          return self.run(**kwargs);
