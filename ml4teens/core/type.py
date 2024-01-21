import copy;
import re;

#=============================================================================================
class Type:

      accepted_names=["Tensor"];
      
      @staticmethod
      def accepted_type(tp, kind):
          if kind=="slot" and type(tp) is set: return True;
          if type(tp) is type: return True;
          if tp.__name__ in Type.accepted_names: return True;
          #print(f"Tipo '{tp}' ({tp.__name__}), desconocido", "__name__" in dir(tp),  tp.__name__ in Type.accepted_names, flush=True);
          return False;
          
      def __init__(self, tipo, clase):
          assert clase=="signal" or clase=="slot", "Las declaraciones de tipos deben ser SIGNAL o SLOT";
          assert Type.accepted_type(tipo, clase), f"Las declaraciones de tipos deben ser definidas como un conjunto (de tipos) o un tipo reconocido: '{tipo.__name__}' es desconocido";

          self._kws={};
          self._class=clase;

          if type(tipo) is set:
             assert clase=="slot", "Si la declaración es un conjunto de tipos, entonces la clase debe ser SLOT, no SIGNAL";
             tipos=tipo;
             assert all([(Type.accepted_type(t,clase)) for t in tipos]), "Si la declaración de un tipo es un conjunto, esta debe ser un conjunto de tipos reconocidos";
             self._type=tipos;
          else:
             self._type=tipo;

      def __str__(self):
          if type(self._type) is set:
             rt="["+(", ".join([str(t) for t in self._type]))+"]";
          else:
             rt=str(self._type);
          return rt;

      def __repr__(self):
          if type(self._type) is set:
             rt="["+(", ".join([str(t) for t in self._type]))+"]";
          else:
             rt=str(self._type);
          return rt;

