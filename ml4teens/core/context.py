import time;

import torch;

from IPython.display import display;
from IPython.display import HTML, Javascript;

from .signalType import SignalType;
from .signals    import Signals;
from .slotType   import SlotType;
from .slots      import Slots;

from ..tools     import debug;

#-------------------------------------------------------------------------------
# Es un singleton
#-------------------------------------------------------------------------------
class Context:

    _instance = None;
    
    #---------------------------------------------------------------------------
    @classmethod
    def __html__(cls):       
        display( HTML(
                      """
                      <!-- JQUERY -->
                      <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
                      
                      <!-- JQUERY UI -->
                      <link rel="stylesheet" href="https://ajax.googleapis.com/ajax/libs/jqueryui/1.13.2/themes/smoothness/jquery-ui.css">
                      <script src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.13.2/jquery-ui.min.js"></script>
                      """
               )     );
        pass;

    #---------------------------------------------------------------------------
    def __new__(cls, *args, **kwargs):
        """
        Crea la única instancia de esta clase.
        
        Si ya existe previamente simplemente devuelve la instancia creada con antelación.
        
        Esto permite que sólo exista una instanca de esta clase, aunque se llame en varias ocasiones.
        """
        if not cls._instance:
           cls._instance = super(Context, cls).__new__(cls);
           cls._instance.listeners={};
           cls._sync=False; # por defecto
           cls._cpu =True;
           cls._gpu =False;
           #cls.__html__();
        return cls._instance;

    #-----------------------------------------------------------------------------------------
    def __init__(self):
        """
        Este es un constructor falso, no hace nada.         
        La inicialización del **único** objeto de esta clase se hace en *__new__*.
        """
        pass;

    #-----------------------------------------------------------------------------------------
    @classmethod
    @property
    def instance(cls):
        return Context() if Context._instance==None else Context._instance;
        
    #-----------------------------------------------------------------------------------------
    @property
    def sync(self):
        context = Context._instance;
        return context._sync;
        
    @sync.setter    
    def sync(self, value):
        context = Context._instance;
        context._sync=bool(value);
        
    #-----------------------------------------------------------------------------------------
    @property
    def cpu(self):
        context = Context._instance;
        return context._cpu;
        
    @cpu.setter    
    def cpu(self, value):
        context = Context._instance;
        assert bool(value) or (not bool(value) and torch.cuda.is_available()), "No diponemos de GPUs, así que no podemos activar esta opción";
        context._cpu=bool(value);
        context._gpu=not context._cpu;
        
    #-----------------------------------------------------------------------------------------
    @property
    def gpu(self):
        context = Context._instance;
        return context._gpu;
        
    @gpu.setter    
    def cpu(self, value):
        context = Context._instance;
        assert (not bool(value)) or (bool(value) and torch.cuda.is_available()), "No diponemos de GPUs, así que no podemos activar esta opción";
        context._gpu=bool(value);
        context._cpu=not context._gpu;
        
    #-----------------------------------------------------------------------------------------
    #@classmethod
    #def notify(cls, message):
    #    #https://notifyjs.jpillora.com/
    #    #https://til.simonwillison.net/jupyter/javascript-in-a-jupyter-notebook
    #    #message=message.replace('"',"'");
    #    #display( Javascript(data=f"""$.notify("{message}");""", lib=["https://rawgit.com/notifyjs/notifyjs/master/dist/notify.js"]) );
    #    pass;

    #-----------------------------------------------------------------------------------------
    def blocks(self):
        blocks=set();
        for signal in self.listeners:
            source, _ = signal;
            blocks.add(source);
            for slot, _ in self.listeners[signal]:
                target, _ = slot;
                blocks.add(target);
        return list(blocks);
    
    #-----------------------------------------------------------------------------------------
    def reset(self):
        for block in self.blocks():
            block.terminate();
        self.listeners={};
        return self;

    #-----------------------------------------------------------------------------------------
    def subscribe(self, signal, slot, mods={}):
        """
        Registra la pareja (*signal*, *slot*) en este contexto.
        
        Si ya existe esta pareja, la elimina y la vuelve a añadir (quizá con otros *mods*).
        
        :param signal:   La señal (*signal*).
        :type  signal:   tupla (*block*, *signal name*)
        :param slot:     El *slot*.
        :type  slot:     Tupla (*block*, *slot name*)
        :param mods:     Modificadores de *signal*/*slot*.
        :type  mods:     dict
        """
        assert signal is not None and type(signal) is tuple and len(signal)==2;
        assert slot   is not None and type(slot  ) is tuple and len(slot  )==2;
        assert type(mods) is dict;
        if not signal in self.listeners: self.listeners[signal]=[];
        self.listeners[signal]=[(s,m) for s,m in self.listeners[signal] if s!=slot];
        self.listeners[signal].append((slot,mods));

    #-----------------------------------------------------------------------------------------
    def unsubscribe(self, signal, slot):
        """
        Elimina la pareja (*signal*, *slot*) en este contexto.
        
        Si no existe esta pareja, no hace nada.
        
        :param signal: La señal (*signal*).
        :type  signal: tupla (*block*, *signal name*)
        :param slot:   El *slot*.
        :type  slot:   tupla (*block*, *slot name*)
        """
        if signal in self.listeners:
           self.listeners[signal]=[(s,m) for s,m in self.listeners[signal] if s!=slot];
           
    #-----------------------------------------------------------------------------------------
    def checkSubscription(self, signal, slot=None):
        """
        Comprueba si se ha registrado la pareja (*signal*, *slot*) en este contexto.
        
        Si *slot* es None, sólo comprueba si está registrado *signal*.
        
        :param signal: La señal (*signal*).
        :type  signal: tupla (*block*, *signal name*)
        :param slot:   El *slot*.
        :type  slot:   tupla (*block*, *slot name*) | None
        :return:       Si *slot* no es None, devuelve si la pareja (*signal*,*slot*) está registrada. Si *slot* es None, devuelve si *signal* tiene *slot*s escuchando.
        :rtype:        True/False
        """
        if slot is not None:
           if signal in self.listeners:        
              for s,m in self.listeners[signal]:
                  if s==slot: return True;
           return False;
        else:
           return signal in self.listeners and self.listeners[signal];
           
    #-----------------------------------------------------------------------------------------
    def newToken(self, data, **kwargs):
        return {"data":data, **kwargs};

    #-----------------------------------------------------------------------------------------
    def emit(self, **kwargs):
        """
        Emite una señal directamente a los 'listeners' de (source,sname) o a un slot (target,sname).
        
        'target' y 'source' son exclusivos y obligatorios (por separado).
        
        :param source: El objeto que envía la señal.
        :type  source: Block
        :param target: El objeto al que se le envía la señal.
        :type  target: Block
        :param sname:  El nombre de una señal/slot (alias: signal_name o slot_name, según sea source/target).
        :type  sname:  str
        :param data:   El dato que acompaña a la señal (alias: value).
        :type  data:   Cualquier cosa.
        :param mods:   Los modificadores, si se trata de el envío de un señal a un slot.
        :type  mods:   dict | None.
        """        
        
        def _sync(block, mods):
            
            rt = self._sync if self._sync is not None else False;
                       
            #if block._requestSync==True : return True ;
            #if block._requestSync==False: rt=False;
            #
            #if     mods.get("sync",False) and not mods.get("no sync",False): return True;
            #if not mods.get("sync",False) and     mods.get("no sync",False): return False;
            
            return rt;
            #-------------------
        
        assert (("source" in kwargs) and ("target" not in kwargs)) or (("source" not in kwargs) and ("target" in kwargs))  or (("source" in kwargs) and ("target" in kwargs));
               
        assert ("sname" in kwargs) or ("signal_name" in kwargs) or ("slot_name" in kwargs);
        
        assert ("data"  in kwargs) or ("value" in kwargs);
        
        if ("target" in kwargs) and ("source" not in kwargs):
           # señal enviada desde el espacio del usuario
           # ha de ejecutarse el slot (sname) correspondiente
           target=kwargs["target"];
           sname=kwargs.get("sname") or kwargs.get("slot_name");
           data =kwargs.get("data" ) or kwargs.get("value"    );
           mods =kwargs.get("mods" ) or {};
           assert type(mods) is dict;
           debug.print(f"Ha llegado un evento del usuario al slot '{sname}' de {target._fullClassName}::{type(data)}, con mods '{mods}'");
           if sname in target.slots:
              slot=target.slots[sname];
              
              if _sync(target,mods):
                 debug.print(f"Ejecutando el slot '{sname}' de {target._fullClassName}, con data={type(data)} y mods='{mods}'");
                 #mods.pop("sync",None);
                 #mods.pop("no sync",None);
                 target.run_sync(time.time(), sname, self.newToken(data), mods);
                 
              else:              
                 debug.print(f"Mandando a {target._fullClassName} una señal al slot '{sname}' con data={type(data)} y mods='{mods}'");
                 #mods.pop("sync",None);
                 #mods.pop("no sync",None);
                 target._queue.put( (time.time(), sname, self.newToken(data), mods) );
                 if not target.running(): target.run();
              
           else:
              raise RuntimeError(f"No existe el slot '{sname}' en {target._fullClassName}");
           
        elif ("source" in kwargs) and ("target" in kwargs):
           # señal enviada por un bloque (source) a otro concreto (target)
           # ha de ejecutarse el slot (sname) correspondiente
           source=kwargs["source"];
           target=kwargs["target"];
           sname=kwargs.get("sname") or kwargs.get("slot_name");
           data =kwargs.get("data" ) or kwargs.get("value"    );
           mods =kwargs.get("mods" ) or {};
           assert type(mods) is dict;
           debug.print(f"Ha llegado un evento al slot '{sname}' de {target._fullClassName}::{type(data)}, con mods '{mods}'");
           if sname in target.slots:
              slot=target.slots[sname];              
              
              if _sync(target,mods):
                 debug.print(f"Ejecutando el slot '{sname}' de {target._fullClassName}, con data={type(data)} y mods='{mods}'");
                 mods.pop("sync",None);
                 mods.pop("no sync",None);
                 target.run_sync(time.time(), sname, self.newToken(data), mods);
                 
              else:              
                 debug.print(f"Mandando a {target._fullClassName} una señal al slot '{sname}' con data={type(data)} y mods='{mods}'");
                 mods.pop("sync",None);
                 mods.pop("no sync",None);
                 target._queue.put( (time.time(), sname, self.newToken(data), mods) );
                 if not target.running(): target.run();
              
           else:
              raise RuntimeError(f"No existe el slot '{sname}' en {target._fullClassName}");
           
        elif ("source" in kwargs) and ("target" not in kwargs):
           # señal generada en un bloque (source)
           # ha de enviarse a todos sus subscriptores
           source=kwargs["source"];
           sname =kwargs.get("sname") or kwargs.get("signal_name");
           data  =kwargs.get("data" ) or kwargs.get("value"      );
           mods  =kwargs.get("mods" ) or {};
           assert type(mods) is dict;
           debug.print(f"{source._fullClassName}:: enviando la señal '{sname}', con data={type(data)}, a todos sus subscriptores");
           signal=(source, sname);
           if signal in self.listeners:
              for slot, _mods in self.listeners[signal]:
                  target, slot_name = slot;
                  debug.print(f"Enviando la señal '{slot_name}', con data={type(data)}, a {target._fullClassName}'");
                  self.emit(source=source, target=target, sname=slot_name, data=data, mods=(mods|_mods));
           else:
              raise RuntimeError(f"No existe la señal '{sname}' en {source._fullClassName}");
               
    #-----------------------------------------------------------------------------------------
    def wait(self, boredtime=1):
    
        while any([(not b._queue.empty() or b.boredTime()<boredtime) for b in self.blocks()]):
              time.sleep(1);
              
        for b in self.blocks():
            b.terminate();
            
    #-----------------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------
    class Linker:

          def __init__(self, block, sname, mods=None):
              from .block import Block;
              assert isinstance(block, Block);
              assert sname and type(sname) is str;
              assert mods is None or isinstance(mods, dict);
              self._block=block;
              self._sname=sname;
              self._mods=mods or {};

          def __rshift__(self, rlinker): # a >> b, no sync
              assert (self._sname in self._block.signals) and (rlinker._sname in rlinker._block.slots);
              assert self._block.signals[self._sname]["type"] == rlinker._block.slots[rlinker._sname]["type"], f"Tipo incompatibles {self._block.signals[self._sname]['type']} != {rlinker._block.slots[rlinker._sname]['type']}";
              self._mods.pop("sync", None);
              self._mods.pop("no sync", None);
              self._mods["sync"   ]=False;
              self._mods["no sync"]=True;
              debug.print(f"Sunscripción: {self._block}:'{self._sname}' >> {rlinker._block}:'{rlinker._sname}'");
              Context.instance.subscribe((self._block,self._sname), (rlinker._block,rlinker._sname), (self._mods|rlinker._mods));
              return rlinker._block;

          def __lshift__(self, rlinker): # a << b, no sync
              assert (self._sname in self._block.slots) and (rlinker._sname in rlinker._block.signals);
              assert self._block.slots[self._sname]["type"] == rlinker._block.signals[rlinker._sname]["type"], f"Tipo incompatibles {self._block.slots[self._sname]['type']} != {rlinker._block.signals[rlinker._sname]['type']}";
              self._mods.pop("sync", None);
              self._mods.pop("no sync", None);
              self._mods["sync"   ]=False;
              self._mods["no sync"]=True;
              debug.print(f"Sunscripción: {rlinker._block}:'{rlinker._sname}' << {self._block}:'{self._sname}'");
              Context.instance.subscribe((rlinker._block,rlinker._sname), (self._block,self._sname), (rlinker._mods|self._mods));
              return self._block;

          def __ge__(self, rlinker): # a >= b, sync
              assert (self._sname in self._block.signals) and (rlinker._sname in rlinker._block.slots);
              assert self._block.signals[self._sname]["type"] == rlinker._block.slots[rlinker._sname]["type"], f"Tipo incompatibles {self._block.signals[self._sname]['type']} != {rlinker._block.slots[rlinker._sname]['type']}";
              self._mods.pop("sync", None);
              self._mods.pop("no sync", None);
              self._mods["sync"   ]=True;
              self._mods["no sync"]=False;
              debug.print(f"Sunscripción: {self._block}:'{self._sname}' >= {rlinker._block}:'{rlinker._sname}'");
              Context.instance.subscribe((self._block,self._sname), (rlinker._block,rlinker._sname), (self._mods|rlinker._mods));
              return rlinker._block;

          def __ge__(self, rlinker): # a >= b, sync
              assert (self._sname in self._block.slots) and (rlinker._sname in rlinker._block.signals);
              assert self._block.slots[self._sname]["type"] == rlinker._block.signals[rlinker._sname]["type"], f"Tipo incompatibles {self._block.slots[self._sname]['type']} != {rlinker._block.signals[rlinker._sname]['type']}";
              self._mods.pop("sync", None);
              self._mods.pop("no sync", None);
              self._mods["sync"   ]=True;
              self._mods["no sync"]=False;
              debug.print(f"Sunscripción: {rlinker._block}:'{rlinker._sname}' <= {self._block}:'{self._sname}'");
              Context.instance.subscribe((rlinker._block,rlinker._sname), (self._block,self._sname), (rlinker._mods|self._mods));
              return self._block;
