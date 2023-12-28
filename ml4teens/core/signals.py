
from .signalType import SignalType

#======================================================================================
class Signals: # name, type, stub

      #--------------------------------------------------------------------------------
      def __init__(self):
          self._signals={};

      #--------------------------------------------------------------------------------
      def __getitem__(self, nombre):
          if nombre in self._signals: return self._signals[nombre];
          else:                       raise KeyError(f"No encuentro la señal '{nombre}'.");

      #--------------------------------------------------------------------------------
      def __delitem__(self, nombre):
          if nombre in self._signals: del self._signals[nombre];
          else:                       raise KeyError(f"No encuentro la señal '{nombre}'.");

      #--------------------------------------------------------------------------------
      def __setitem__(self, nombre, tipo):
          assert isinstance(tipo, SignalType), ValueError(f"La señal '{nombre}' debe ir acompañada de un tipo en forma de objeto SignalType");
          self._signals[nombre]={ "name":nombre, "type":tipo, "stub":None };

      #--------------------------------------------------------------------------------
      def __len__(self):
          return len(self._signals);

      #--------------------------------------------------------------------------------
      def __iter__(self):
          return iter(self._signals);

      #--------------------------------------------------------------------------------
      def __contains__(self, nombre):
          return nombre in self._signals;

