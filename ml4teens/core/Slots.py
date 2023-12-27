
from . import SlotType;

#======================================================================================
class Slots: # name, type, required, value, default, stub

      #--------------------------------------------------------------------------------
      def __init__(self):
          self._slots={};

      #--------------------------------------------------------------------------------
      def __getitem__(self, nombre):
          if nombre in self._slots: return self._slots[nombre];
          else:                     raise KeyError(f"No encuentro el slot '{nombre}'.");

      #--------------------------------------------------------------------------------
      def __delitem__(self, nombre):
          if nombre in self._slots: del self._slots[nombre];
          else:                     raise KeyError(f"No encuentro el slot '{nombre}'.");

      #--------------------------------------------------------------------------------
      def __setitem__(self, nombre, tipo):
          assert type(tipo)==dict or isinstance(tipo, SlotType), ValueError(f"El slot '{nombre}' debe ir acompañada de un tipo en forma de dict o SlotType");
          if type(tipo)==dict:
             _kws=tipo;
             tipo=None;
             expected_keys = {"type", "required", "default", "stub"};
             if not set(_kws).issubset(expected_keys): raise ValueError(f"Error en la definición del slot '{nombre}': {str(tipo)}");
             if "type"     in _kws: tipo=_kws["type"];
             else:                  raise ValueError(f"Error en la definición del slot '{nombre}': debe indicarse el tipo mediante 'type'");
             if "required" in _kws: required=_kws["required"] ;
             else:                  required=False;
             if "default"  in _kws: default=_kws["default"];
             else:                  default=None;
             if "stub"     in _kws: stub=_kws["stub"];
             else:                  stub=None;
             assert type(tipo)     is SlotType,   ValueError(f"Error en la definición del slot '{nombre}': 'type' debe ser un objeto de tipo SlotType");
             assert type(required) in [bool,int], ValueError(f"Error en la definición del slot '{nombre}': 'required' debe ser un boleano o un número entero");
             self._slots[nombre]={"name":nombre, "type":tipo, "required":required, "default":default, "stub":stub };
          else:
             assert isinstance(tipo, SlotType);
             self._slots[nombre]={"name":nombre, "type":tipo, "required":False, "default":None, "stub":None };

      #--------------------------------------------------------------------------------
      def __len__(self):
          return len(self._slots);

      #--------------------------------------------------------------------------------
      def __iter__(self):
          return iter(self._slots);

      #--------------------------------------------------------------------------------
      def __contains__(self, nombre):
          return nombre in self._slots;

      #--------------------------------------------------------------------------------
      def groups(self):
          rt={};
          for key in self._slots:
              if   self._slots[key]["required"]==False or self._slots[key]["required"]==0:
                   if 0 not in rt: rt[0]=[];
                   rt[0].append(key);
              elif self._slots[key]["required"]==True  or self._slots[key]["required"]==1:
                   if 1 not in rt: rt[1]=[];
                   rt[1].append(key);
              else:
                   r=self._slots[key]["required"];
                   if r not in rt: rt[r]=[];
                   rt[r].append(key);
          return rt;

      #--------------------------------------------------------------------------------
      def iscomplete(self, values):
          G=self.groups(); #TODO pre-calcular esta variable
          for idx in G:
              if   idx==0: continue;
              elif idx==1:
                   if not all([(values[k] is not None) if k in values else False for k in G[idx]]): return False;
              else:
                   if not any([(values[k] is not None) if k in values else False for k in G[idx]]): return False;
          return True;
