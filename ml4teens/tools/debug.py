import builtins;
import traceback;

_enabled=False;

#===============================================================================
def _notebook():
    try:
        from IPython import get_ipython;
        ipython = get_ipython();
        if 'IPKernelApp' not in ipython.config: return False;
        if 'VSCODE_PID' in os.environ:          return False;
        return True
    except (ImportError, AttributeError):
        return False

#===============================================================================
def enable():
    global _enabled;
    _enabled=True;

#-------------------------------------------------------------------------------
def disable():
    global _enabled;
    _enabled=False;
   
#-------------------------------------------------------------------------------
def print(*args, **kwargs):    
    exception=kwargs.pop("exception",None);
    if _enabled or exception:
       if "flush" not in kwargs: kwargs["flush"]=True;
       builtins.print(*args, **kwargs);
       if exception:
         detalles_excepcion = traceback.format_exception(type(exception), exception, exception.__traceback__)
         mensaje_amigable = "".join(detalles_excepcion)
         print(mensaje_amigable, flush=True);
       