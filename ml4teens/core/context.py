from IPython.display import display;
from IPython.display import HTML, Javascript;

from .signalType import SignalType;
from .signals    import Signals;
from .slotType   import SlotType;
from .slots      import Slots;

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
           cls.__html__();
        return cls._instance;

    #-----------------------------------------------------------------------------------------
    def __init__(self):
        """
        Este es un constructor falso, no hace nada, ya que la inicialización del objeto se hace en *__new__*.
        """
        pass;

    #-----------------------------------------------------------------------------------------
    @classmethod
    @property
    def instance(cls):
        return Context() if Context._instance==None else Context._instance;
        
    #-----------------------------------------------------------------------------------------
    #TODO doesn't work!
    @classmethod
    def notify(cls, message):
        #https://notifyjs.jpillora.com/
        #https://til.simonwillison.net/jupyter/javascript-in-a-jupyter-notebook
        #message=message.replace('"',"'");
        #display( Javascript(data=f"""$.notify("{message}");""", lib=["https://rawgit.com/notifyjs/notifyjs/master/dist/notify.js"]) );
        pass;

    #-----------------------------------------------------------------------------------------
    def reset(self):
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
    def emit(self, objeto, sname, data, check=True):
        """
        Emite una señal, bien como signal o como slot.
        
        :param objeto: El objeto que recibe/envía la señal o el slot.
        :type  objeto: Block
        :param sname:  Dependiendo de 'check' es el nombre de una señal (check==True) o de un slot (check==False).
        :type  sname:  str
        :param data:   El dato que acompaña a la señal o slot.
        :type  data:   Cualquier cosa menos None.
        :param check:  Si True se envía una señal a los 'listeners' de (objeto,sname); si False se simula una señal al slot (objeto,sname).
        """
        if check and (objeto, sname) in self.listeners:
           for (target, slot_name) in self.listeners[(objeto, sname)]:
               slot=target.slots[slot_name];
               data=data if data is not None else slot["default"];
               target._values[slot_name] = data;
               if target.slots.iscomplete(target._values):
                  func=slot["stub"];
                  func(target, slot_name, data);
        else:
           target=objeto;
           slot=target.slots[sname];
           data=data if data is not None else slot["default"];
           target._values[sname] = data;
           if target.slots.iscomplete(target._values):
              func=slot["stub"];
              func(target, sname, data);

    #-----------------------------------------------------------------------------------------
    def run(self, objeto, **kwargs):
        try:
           if hasattr(objeto,"run") and callable(getattr(objeto, "run")):
              objeto.run(**kwargs);
           else:
              raise RuntimeError("Error: el objeto que intentas ejecutar no tiene un método 'run'");
        except KeyboardInterrupt as e:
           pass;       

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
