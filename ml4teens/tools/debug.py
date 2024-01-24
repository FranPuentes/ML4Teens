import sys, io;
import builtins;
import traceback;

_enabled=False;
_startsWith=None;

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
def enable(startsWith:str=None):
    global _enabled;
    global _startsWith;
    _enabled=True;
    _startsWith=startsWith if (type(startsWith) is str and bool(startsWith)) else None;

#-------------------------------------------------------------------------------
def disable():
    global _enabled;
    global _startsWith;
    _enabled=False;
    _startsWith=None;
   
#-------------------------------------------------------------------------------
def print(*args, **kwargs):
    exception=kwargs.pop("exception",None);
    if _enabled or exception:
       buffer = io.StringIO();
       try:
         stdout=sys.stdout;
         sys.stdout=buffer;
         builtins.print(*args, **kwargs);         
         if exception:
            detalles_excepcion = traceback.format_exception(type(exception), exception, exception.__traceback__)
            mensaje_amigable = "".join(detalles_excepcion)
            builtins.print(mensaje_amigable);
         sys.stdout.flush();
                        
       finally:
         sys.stdout=stdout;
         message=buffer.getvalue();         
         global _startsWith;         
         if _startsWith is None or (_startsWith is not None and message.startswith(_startsWith)):
            builtins.print(message, end='', flush=True);
         buffer.close();   
         