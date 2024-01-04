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
        La inicialización del objeto se hace en *__new__*.
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
            for slot in self.listeners[signal]:
                target, _ = slot;
                blocks.add(target);
        return list(blocks);
    
    #-----------------------------------------------------------------------------------------
    def reset(self):        
        for block in self.blocks():
            block.terminate(clear_all=True);
        self.listeners = {};
        return self;

    #-----------------------------------------------------------------------------------------
    def subscribe(self, event, listener):
        """
        Registra la pareja (*event*, *listener*) en este contexto.
        Si ya existe esta pareja, no hace nada.
        
        :param event:    La señal (*signal*).
        :type  event:    tupla (*block*, *signal name*)
        :param listener: El *slot*.
        :type  listener: tupla (*block*, *slot name*)
        :return:         True si ha añadido la pareja, False si ya existía (y no la ha añadido).
        :rtype:          bool
        """
        if event not in self.listeners: self.listeners[event] = [];
        if listener in self.listeners[event]: return False;
        self.listeners[event].append(listener);
        return True;

    #-----------------------------------------------------------------------------------------
    def unsubscribe(self, event, listener):
        """
        Elimina la pareja (*event*, *listener*) en este contexto.
        Si no existe esta pareja, no hace nada.
        
        :param event:    La señal (*signal*).
        :type  event:    tupla (*block*, *signal name*)
        :param listener: El *slot*.
        :type  listener: tupla (*block*, *slot name*)
        :return:         True si ha eliminado la pareja, False si no existía previamente.
        :rtype:          bool
        """
        if event in self.listeners:
           if listener in self.listeners[event]:
              self.listeners[event].remove(listener);
              return True;
        return False;
           
    #-----------------------------------------------------------------------------------------
    def checkSubscription(self, event, listener=None):
        """
        Comprueba si se ha registrado la pareja (*event*, *listener*) en este contexto.
        Si *listener* es None, sólo comprueba si está registrado *event*.
        
        :param event:    La señal (*signal*).
        :type  event:    tupla (*block*, *signal name*) | None
        :param listener: El *slot*.
        :type  listener: tupla (*block*, *slot name*)
        """
        return (event in self.listeners and len(self.listeners[event])>0) and (listener is None or listener in self.listeners[event]);

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
        :type  data:   Cualquier cosa menos None.
        """        
        assert (("source" in kwargs) and ("target" not in kwargs)) or (("source" not in kwargs) and ("target" in kwargs));
        assert ("sname" in kwargs) or ("signal_name" in kwargs) or ("slot_name" in kwargs);
        assert ("data"  in kwargs) or ("value" in kwargs);
        
        if "target" in kwargs:
           target=kwargs["target"];
           sname=kwargs.get("sname") or kwargs.get("slot_name");
           data =kwargs.get("data" ) or kwargs.get("value"    );
           assert sname is not None;
           debug.print(f"Ha llegado un evento al slot '{sname}' de {target._fullClassName}::{type(data)}");
           if sname in target.slots:
              slot=target.slots[sname];
              # TODO comprobar que tipo de 'data' se corresponda con el slot
              if not target.running(): target.run();
              debug.print(f"{target._fullClassName}:: invocando el slot '{sname}' con data={type(data)}");
              target._queue.put( (time.time(), sname, data) );
           else:
              debug.print(f"No existe el slot '{sname}' en {target._fullClassName}");
              pass;
           
        else:
           source=kwargs["source"];
           sname=kwargs.get("sname") or kwargs.get("signal_name");
           data =kwargs.get("data" ) or kwargs.get("value"      );
           assert sname is not None;
           debug.print(f"{source._fullClassName}:: enviando la señal '{sname}', con data={type(data)}, a todos sus listeners");
           if (source, sname) in self.listeners:
              for (target, slot_name) in self.listeners[(source, sname)]:
                  debug.print(f"Enviando la señal '{slot_name}', con data={type(data)}, a {target._fullClassName}");
                  self.emit(target=target, sname=slot_name, data=data);
               
              """
               slot=target.slots[slot_name];
               group=slot["required"];
               data=data if data is not None else slot["default"];
               target._values[slot_name] = data;
               complete_slots=target.slots.iscomplete(target._values);
               if group==False or (bool(complete_slots) and (group in complete_slots) and (slot_name in complete_slots[group])):
                  #print(" "*5, f"LISTENER: {Block._classNameFrom(target.__init__)}({slot_name})", end=', ', flush=True);
                  #print(f"data is None:{bool(data is None)}", end=', ', flush=True);
                  #print(f"COMPLETE: {complete_slots}", flush=True);
                  func=slot["stub"];
                  func(target, slot_name, data);
               else:
                  #print(" "*5, f"LISTENER: {Block._classNameFrom(target.__init__)}({slot_name})", end=', ', flush=True);
                  #print(f"data is None:{bool(data is None)}", end=', ', flush=True);
                  #print(f"IS INCOMPLETE!", flush=True);
                  pass;
              """
    #-----------------------------------------------------------------------------------------
    def wait(self, boredtime=5):
    
        while any([(not b._queue.empty() or b.boredTime()<boredtime) for b in self.blocks()]):
              time.sleep(1);
              
        for block in self.blocks():
            block.terminate(clear_all=True);
            
    """
    def accept(self, target, sname, data):
        " ""
        Encola un evento (sname,data) en el objeto indicado por 'target'.
        Si 'target' no se está ejecutando, se inicia.
        
        :param target: El objeto que recibe la señal y posee el slot.
        :type  target: Block
        :param sname:  El nombre del slot.
        :type  sname:  str
        :param data:   El dato que acompaña a la señal.
        :type  data:   Cualquier cosa menos None.
        " ""
        if not target.running():
           target.run();
        
        if sname in target.slots:
           slot=target.slots[sname];
           # comprobar que tipo de 'data' se corresponda con el slot
           target._queue.put( (time.time(), sname, data) );
        else:
           # el slot no existe en target.
           pass;   
           
        #if sname in target.slots:
        #   slot=target.slots[sname];
        #   group=slot["required"];
        #   data=data if data is not None else slot["default"];
        #   target._values[sname]=data;
        #   complete_slots=target.slots.iscomplete(target._values);
        #   assert group in complete_slots;
        #   if bool(complete_slots) and (sname in complete_slots[group]):
        #      #func=slot["stub"];
        #      #func(target, sname, data);
    """
    
    #-----------------------------------------------------------------------------------------
    #def run(self, *args, **kwargs):
    #    try:
    #       for objeto in args:
    #           if hasattr(objeto,"run") and callable(getattr(objeto, "run")):
    #              objeto.run(**kwargs);
    #           else:
    #              raise RuntimeError("Error: el objeto que intentas ejecutar no tiene un método 'run'");
    #              
    #    except KeyboardInterrupt as e:
    #       pass;       

    #-----------------------------------------------------------------------------------------
    class Linker:

          def __init__(self, block, sname):
              from .block import Block;
              assert isinstance(block, Block) and type(sname) is str;
              self._block=block;
              self._sname=sname;

          def __rshift__(self, rlinker):
              assert (self._sname in self._block.signals) and (rlinker._sname in rlinker._block.slots);
              assert self._block.signals[self._sname]["type"] == rlinker._block.slots[rlinker._sname]["type"], f"Tipo incompatibles {self._block.signals[self._sname]['type']} != {rlinker._block.slots[rlinker._sname]['type']}";
              Context.instance.subscribe((self._block,self._sname), (rlinker._block,rlinker._sname));
              return rlinker._block;

          def __lshift__(self, rlinker):
              assert (self._sname in self._block.slots) and (rlinker._sname in rlinker._block.signals);
              assert self._block.slots[self._sname]["type"] == rlinker._block.signals[rlinker._sname]["type"], f"Tipo incompatibles {self._block.slots[self._sname]['type']} != {rlinker._block.signals[rlinker._sname]['type']}";
              Context.instance.subscribe((rlinker._block,rlinker._sname), (self._block,self._sname));
              return self._block;
