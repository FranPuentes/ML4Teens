
from . import Block
from . import SignalType, Signals
from . import SlotType,   Slots

#-------------------------------------------------------------------------------
# Es un singleton
#-------------------------------------------------------------------------------
class Context:

    _instance = None;

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
           cls._instance = super(Context, cls).__new__(cls);
           cls._instance.listeners={};
        return cls._instance;

    def __init__(self):
        pass;

    @classmethod
    @property
    def instance(cls):
        return Context() if Context._instance==None else Context._instance;

    def reset(self):
        self.listeners = {};
        return self;

    def subscribe(self, event, listener):
        if event not in self.listeners: self.listeners[event] = [];
        self.listeners[event].append(listener);

    def unsubscribe(self, event, listener):
        if event in self.listeners:
           self.listeners[event].remove(listener);

    def emit(self, objeto, signal_name, data):
        if (objeto, signal_name) in self.listeners:
           for (target, slot_name) in self.listeners[(objeto, signal_name)]:
               slot=target.slots[slot_name];
               data=data if data is not None else slot["default"];
               target._values[slot_name] = data;
               if target.slots.iscomplete(target._values):
                  func=slot["stub"];
                  func(target, slot_name, data);

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
              assert isinstance(block, Block) and type(sname) is str;
              self._block=block;
              self._sname=sname;

          def __rshift__(self, rlinker):
              assert (self._sname in self._block.signals) and (rlinker._sname in rlinker._block.slots);
              assert self._block.signals[self._sname]["type"] == rlinker._block.slots[rlinker._sname]["type"];
              Context.instance.subscribe((self._block,self._sname), (rlinker._block,rlinker._sname));
              return rlinker._block;

          def __lshift__(self, rlinker):
              assert (self._sname in self._block.slots) and (rlinker._sname in rlinker._block.signals);
              assert self._block.slots[self._sname]["type"] == rlinker._block.signals[rlinker._sname]["type"];
              Context.instance.subscribe((rlinker._block,rlinker._sname), (self._block,self._sname));
              return self._block;
