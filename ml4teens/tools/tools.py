import sys, os, io;
from PIL import Image;
import requests;
from io import BytesIO;
import tempfile;

#===============================================================================
def image_from_url(url:str, mode:str=None, width:int=None, height:int=None):
    """
    Esta función recibe como parámetro una url:str y si es posible devuelve una imagen:Image.
    
    Si se indica el mode:str, se convertirá la imagen a dicho formato.
    
    Si se indica width:int o height:int, se redimensionará la imagen.
    
    Si no puede devolver la imagen dispara una excepción.
    """
    try:
      headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'};

      response = requests.get(url, headers=headers);      
      if response.status_code == 200:
         img = Image.open(BytesIO(response.content));
         
         img.load();
         
         if width is not None or height is not None:
         
            original_width, original_height = img.size;
         
            if width is not None and height is None:
               ratio = width / original_width;
               new_height = int(original_height * ratio);
               new_dimensions = (width, new_height);
           
            elif height is not None and width is None:
               ratio = height / original_height;
               new_width = int(original_width * ratio);
               new_dimensions = (new_width, height);
           
            else:
               new_dimensions = (width, height);
               
            img = img.resize(new_dimensions, Image.ANTIALIAS);
         
         if mode is not None: return img.convert(mode);
         else:                return img;
         
      else:
         raise RuntimeError(f"Error al descargar la imagen: Estado HTTP {response.status_code}");
        
    except Exception as e:
        raise RuntimeError(f"No he podido cargar la siguiente imagen: {url}");

imageFromUrl = image_from_url;

#===============================================================================
def runnigInGoogleColab():
    """
    Averigua si estamos en un ambiente Google Colab.
    """
    if 'google.colab' in sys.modules: return True;
    else:                             return False;

#-------------------------------------------------------------------------------
def runnigInJupyterLike():
    """
    Averigua si estamos en un ambiente Jupyter Notebook.
    """
    try:
        from IPython import get_ipython;
        if 'IPKernelApp' in get_ipython().config: return True;
    except:
        pass    
    return False;
    
#-------------------------------------------------------------------------------
def runningInNotebook():
    """
    Averigua si estamos en un ambiente Notebook genérico.
    """
    try:
        from IPython import get_ipython;
        if get_ipython() is not None: return True
    except ImportError:
        return False    
    return False
    
#===============================================================================
def uploadFiles():
    """
    Invita al usuario a subir ficheros (local -> Colab/Jupyter).
    
    Detecta si estamos en un ambiente Colab o Jupyter.
    
    Permite subir varios ficheros de cualquier tipo.
    """
    _files=[];
    if runnigInGoogleColab():
       from google.colab import files;
       uploaded = files.upload();
       for filename in uploaded.keys():
           _files.append(filename);
    else:
       import ipywidgets as widgets;
       uploader = widgets.FileUpload(accept='*/*', multiple=True);
       display(uploader);
       for item in uploader.value:
           _files.append(item["name"]);

    return tuple(_files);

#===============================================================================
class UrlDownload:

      def __init__(self, url:str, filename=None, autoremove=True):
          self._autoremove=autoremove;
          response = requests.get(url);
          response.raise_for_status();
          if filename is None:
             with tempfile.NamedTemporaryFile(delete=False, delete_on_close=False) as temp:
                  temp.write(response.content);
                  self._filename=temp.name;
          else:
             with open(filename,"wb") as fd:
                  fd.write(response.content);
                  self._filename=filename;

      def __del__(self):
          try:
            if self._autoremove:
               os.remove(self._filename);
          except:
            pass;

      def __str__(self):
          return self._filename;

      @property
      def filename(self):
          return self._filename;

      @property
      def autoremove(self):
          return self._autoremove;


#===============================================================================
def searchFilename(path, filename):
    """
    Busca un archivo de forma recursiva en un directorio y devuelve su path absoluto.

    :param path: El path del directorio en el que empezar la búsqueda.
    :param filename: El nombre del archivo a buscar.
    :return: El path absoluto del archivo si se encuentra, o None si no se encuentra.
    """
    for raiz, directorios, archivos in os.walk(path):
        if filename in archivos:
           return os.path.join(raiz, nombre_archivo);
    return None;
    