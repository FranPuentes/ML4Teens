import time;

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
    def subscribe(self, signal, slot, mods=None):
        """
        Registra la pareja (*signal*, *slot*) en este contexto.
        
        Si ya existe esta pareja, la elimina y la vuelve a añadir (quizá con otros *mods*).
        
        :param signal:   La señal (*signal*).
        :type  signal:   tupla (*block*, *signal name*)
        :param slot:     El *slot*.
        :type  slot:     Tupla (*block*, *slot name*)
        :param mods:     Modificadores de la instancia *signal*/*slot*.
        :type  mods:     Cualquier cosa.
        """
        assert signal is not None and type(signal) is tuple and len(signal)==2;
        assert slot   is not None and type(slot  ) is tuple and len(slot  )==2;
        if signal not in self.listeners: self.listeners[signal] = [];
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
        if signal not in self.listeners: return False;
        
        if slot is not None:
           for s,m in self.listeners[signal]:
               if s==slot: return True;
           return False;
        else:
           return bool(self.listeners[signal]);
           
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
        def combine_mods(a, b):
            assert isinstance(a,(type(None),dict)), ValueError(f"Context:emit:: Los 'mods' deben ser dict o None: {a}");
            assert isinstance(b,(type(None),dict)), ValueError(f"Context:emit:: Los 'mods' deben ser dict o None: {b}");
            if a is None: return b;
            if b is None: return a;
            return (a|b);
        
        assert (("source" in kwargs) and ("target" not in kwargs)) or (("source" not in kwargs) and ("target" in kwargs));
        assert ("sname" in kwargs) or ("signal_name" in kwargs) or ("slot_name" in kwargs);
        assert ("data"  in kwargs) or ("value" in kwargs);
        
        if "target" in kwargs:
           target=kwargs["target"];
           sname=kwargs.get("sname") or kwargs.get("slot_name");
           data =kwargs.get("data" ) or kwargs.get("value"    );
           mods =kwargs.get("mods" );
           debug.print(f"Ha llegado un evento al slot '{sname}' de {target._fullClassName}::{type(data)}, con mods '{mods}'");
           if sname in target.slots:
              slot=target.slots[sname];
              debug.print(f"{target._fullClassName}:: invocando el slot '{sname}' con data={type(data)} y mods='{mods}'");
              
              if mods and mods.get("sync",False):
                 #if mods: mods["sync"]=None;
                 target.run_sync(time.time(), sname, self.newToken(data), mods);
                 
              else:              
                 #if mods: mods["sync"]=None;
                 target._queue.put( (time.time(), sname, self.newToken(data), mods) );
                 if not target.running(): target.run();
              
           else:
              raise RuntimeError(f"No existe el slot '{sname}' en {target._fullClassName}");
           
        else:
           source=kwargs["source"];
           sname=kwargs.get("sname") or kwargs.get("signal_name");
           data =kwargs.get("data" ) or kwargs.get("value"      );
           mods =kwargs.get("mods" );
           debug.print(f"{source._fullClassName}:: enviando la señal '{sname}', con data={type(data)}, a todos sus listeners");
           signal=(source, sname);
           if signal in self.listeners:
              for slot, slot_mods in self.listeners[signal]:
                  target, slot_name = slot;
                  mods=combine_mods(slot_mods, mods);
                  debug.print(f"Enviando la señal '{slot_name}', con data={type(data)}, a {target._fullClassName} y mods='{mods}'");                  
                  self.emit(target=target, sname=slot_name, data=data, mods=mods);
           else:
              raise RuntimeError(f"No existe la señal '{sname}' en {source._fullClassName}");
               
    #-----------------------------------------------------------------------------------------
    def wait(self, boredtime=2):
    
        while any([(not b._queue.empty() or b.boredTime()<boredtime) for b in self.blocks()]):
              time.sleep(1);
              
        for b in self.blocks():
            b.terminate();
            
    #-----------------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------
    class Linker:

          def __init__(self, block, sname, mods=None):
              from .block import Block;
              assert isinstance(block, Block) and type(sname) is str;
              self._block=block;
              self._sname=sname;
              self._mods = {} if mods is None else dict(mods);

          def __rshift__(self, rlinker):
              assert (self._sname in self._block.signals) and (rlinker._sname in rlinker._block.slots);
              assert self._block.signals[self._sname]["type"] == rlinker._block.slots[rlinker._sname]["type"], f"Tipo incompatibles {self._block.signals[self._sname]['type']} != {rlinker._block.slots[rlinker._sname]['type']}";
              mods=self._mods | rlinker._mods;
              Context.instance.subscribe((self._block,self._sname), (rlinker._block,rlinker._sname), mods);
              return rlinker._block;

          def __lshift__(self, rlinker):
              assert (self._sname in self._block.slots) and (rlinker._sname in rlinker._block.signals);
              assert self._block.slots[self._sname]["type"] == rlinker._block.signals[rlinker._sname]["type"], f"Tipo incompatibles {self._block.slots[self._sname]['type']} != {rlinker._block.signals[rlinker._sname]['type']}";
              mods=self._mods | rlinker._mods;
              Context.instance.subscribe((rlinker._block,rlinker._sname), (self._block,self._sname), mods);
              return self._block;
