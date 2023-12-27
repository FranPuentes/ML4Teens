import random;
import string;

from abc import ABC, abstractmethod;

from . import SignalType, SlotType;

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
              #assert name not in Block._slots[cls], ValueError(f"Slot duplicado: '{name}' en '{cls}'");
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
              #assert name not in Block._signals[cls], f"Signal duplicada: '{name}' en '{cls}'";
              Block._signals[cls][name]=SignalType(typedecl);
              def wrapper(self, data):
                  data=func(self,data);
                  Context.instance.emit(self,name,data);
              return wrapper;
          return decorador;

      #-------------------------------------------------------------------------
      def reset(self, *args):
          if len(args)==0:
             self._values={};
          else:
             for k in args: self._values[k]=None;

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
