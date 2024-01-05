import builtins;

_enabled=False;

def enable():
    global _enabled;
    _enabled=True;

def disable():
    global _enabled;
    _enabled=False;
   
def print(*args, **kwargs):
    if _enabled:       
       if "flush" not in kwargs: kwargs["flush"]=True;
       builtins.print(*args, **kwargs);
       