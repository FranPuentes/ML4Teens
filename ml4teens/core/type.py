import copy;
import re;

#=============================================================================================
class Type:

      def __init__(self, tipo, clase):
          assert clase=="signal" or clase=="slot", "Las declaraciones de tipos deben ser SIGNAL o SLOT";
          assert type(tipo) is set or type(tipo) is type, "Las declaraciones de tipos deben ser definidas como un conjunto (de tipos) o un tipo simple";

          self._kws={};
          self._class=clase;

          if type(tipo) is set:
             assert clase=="slot", "Si la declaración es un conjunto de tipos, entonces la clase debe ser SLOT, no SIGNAL";
             tipos=tipo;
             assert all([(type(t) is type) for t in tipos]), "Si la declaración de un tipo es un conjunto, esta debe ser un conjunto de tipos";
             self._type=tipos;
          else:
             assert type(tipo) is type;
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

