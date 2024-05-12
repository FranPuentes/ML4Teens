# -*- coding: utf-8 -*-
import sys, os, io;
import fnmatch;
import numpy as np;
from PIL import Image;
import requests;
from io import BytesIO;
import tempfile;
import time;
import socket;
import glob;
import json;
import shutil;
import zipfile;
import imageio;

from itertools import accumulate;

#===============================================================================
def imageFromUrl(url:str, mode:str=None, width:int=None, height:int=None):
    """
    Esta función recibe como parámetro una url:str y si es posible devuelve una imagen:Image.
    
    Si se indica el mode:str, se convertirá la imagen a dicho formato.
    
    Si se indica width:int o height:int, se redimensionará la imagen.
    
    Si no puede devolver la imagen dispara una excepción.
    """
    try:
      """
      img = imageio.v3.imread(url);

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
            
         img = img.resize(new_dimensions, Image.Resampling.LANCZOS);
      
      if mode is not None: return img.convert(mode);
      else:                return img;
      """
      
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
               
            img = img.resize(new_dimensions, Image.Resampling.LANCZOS);
         
         if mode is not None: return img.convert(mode);
         else:                return img;
         
      else:
         raise RuntimeError(f"Error al descargar la imagen: Estado HTTP {response.status_code}");
         
    except Exception as e:
      raise RuntimeError(f"No he podido cargar la siguiente imagen: {url}");

#===============================================================================
def runningOnColab():
    """
    Averigua si estamos en un ambiente Google Colab.
    """
    if 'google.colab' in sys.modules: return True;
    else:                             return False;

#-------------------------------------------------------------------------------
def runningOnJupyter():
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
def runningOnNotebook():
    """
    Averigua si estamos en un ambiente Notebook genérico.
    """
    try:
        from IPython import get_ipython;
        if get_ipython() is not None: return True
    except ImportError:
        return False    
    return False

#-------------------------------------------------------------------------------
"""
def runningOnLocal():

    try:
      import netifaces;
      for interface in netifaces.interfaces():
          addresses = netifaces.ifaddresses(interface);
          ipv4 = addresses.get(netifaces.AF_INET, []);
          for address in ipv4:
              ip = address.get('addr');
              if ip == host_ip or ip.startswith("127."):
                 return True
                 
    except ImportError:
      pass;
              
    return False;
"""
#===============================================================================
def uploadFiles(accept=None):
    """
    Invita al usuario a subir ficheros (local -> Colab/Jupyter).
    
    Detecta si estamos en un ambiente Colab o Jupyter.
    
    Permite subir varios ficheros de cualquier tipo.
    """
    _files=[];
    
    if runningOnColab():
       from google.colab import files;
       uploaded = files.upload();
       for filename in uploaded.keys():
           _files.append(filename);
    else:    
       from jupyter_ui_poll import ui_events;
       import ipywidgets as widgets;
       uploader = widgets.FileUpload(accept=accept or '*/*', multiple=True);
       
       _finish=False;
       
       def on_change(change):
           nonlocal _files, _finish;
           _files=list(uploader["new"].keys());
           _finish=True;
       
       display(uploader);
       
       uploader.observe(on_change, names=['value']);   
       with ui_events() as poll:
            while not _finish:
                  poll(50);
                  time.sleep(0.2);
       
    return tuple(_files);

#===============================================================================
class UrlDownload:

      def __init__(self, url:str, filename=None, autoremove=True):
          
          if url.startswith("http"):
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
          else:
             assert filename is None, "Si 'url' es un fichero, no debe indicarse el parámetro 'filename'";
             self._autoremove=False;
             self._filename=url;
          
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
           return os.path.join(raiz, filename);
    return None;

#===============================================================================
def searchPattern(path, pattern):
    """
    Busca archivos de forma recursiva en un directorio y devuelve su path absoluto.

    :param path: El path del directorio en el que empezar la búsqueda.
    :param pattern: El patrón del nombre de los archivos a buscar.
    :return: Una lista con los paths absolutos de los archivos.
    """
    rt=[];
    for raiz, directorios, archivos in os.walk(path):
        for archivo in archivos:
            if fnmatch.fnmatch(archivo, pattern):
               rt.append(os.path.join(raiz, archivo));
    return rt;

#===============================================================================
class CocoDataset:

      def __init__(self, dataset:str):
          assert os.path.isdir(dataset), f"No existe el directorio del dataset: {dataset}";
          self._dataset = dataset;
          files = glob.glob(os.path.join(dataset, '*.json'), recursive=False);
          assert len(files)==1, "No encuentro el fichero (*.json) de anotaciones";
          imagesPath = os.path.join(dataset, 'images');
          assert os.path.isdir(imagesPath), "No existe el directorio 'images' en el dataset";          
          self._annotations = self._load_annotations(files[0]);

      def _load_annotations(self, filename):
          with open(filename, 'r', encoding='utf-8') as fd:
               data = json.load(fd);
               return data;

      def _split(self, l, f=(80,15,5)):
          assert type(l) is int and l>=3;
          assert len(f)==3 and all([type(n) is int for n in f]);
          assert sum(f)==100, f"El split '{f}' debe sumar 100";
          f=list(accumulate([0]+[int(l*n/100.0) for n in f]));
          r=list(range(0,l));
          return set(r[:f[1]]), set(r[f[1]:f[2]]), set(r[f[2]:]);

      def export(self, target, to="yolo", split=(80,15,5), compress=False):
          if target.endswith('.zip'):
             target=os.path.abspath(target);
             path, filename = os.path.split(target);
             basename, ext = os.path.splitext(filename);
             assert not os.path.exists(os.path.join(path,basename)), f"El path '{os.path.join(path,basename)}' existe";
             target=os.path.join(path,basename);
             compress=True;

          if to.lower()=="yolo":
             os.makedirs(target, exist_ok=True);
             os.makedirs(os.path.join(target,"train"), exist_ok=True);
             os.makedirs(os.path.join(target,"val"  ), exist_ok=True);
             os.makedirs(os.path.join(target,"test" ), exist_ok=True);
             images     =sorted(self._annotations["images"     ],key=lambda x: x["id"]);
             annotations=sorted(self._annotations["annotations"],key=lambda x: x["image_id"]);
             train,val,test=self._split(len(images),split);
             for i, image in enumerate(images):
                 if   i in train: dest=os.path.join(target,"train");
                 elif i in val:   dest=os.path.join(target,"val");
                 elif i in test:  dest=os.path.join(target,"test");
                 else:            raise RuntimeError("Error interno");
                 shutil.copy(os.path.join(self._dataset,image["file_name"]), dest);
                 
                 width =image["width" ];
                 height=image["height"];
                 
                 ann=[];
                 for annotation in annotations:
                     if annotation["image_id"] == image["id"]:
                        label_id =annotation["category_id"];
                        x1,y1,w,h=annotation["bbox"];
                        assert label_id>0;
                        ann.append({"id":label_id-1,
                                    "cx":(x1+w/2)/width,
                                    "cy":(y1+h/2)/height,
                                    "bw":(w/width),
                                    "bh":(h/height),
                                   });
                 
                 basename    = os.path.join(self._dataset,image["file_name"]);
                 basename    = os.path.basename(basename);
                 basename, _ = os.path.splitext(basename);
                 basename    = f"{basename}.txt";
                 with open(os.path.join(dest,basename),"wt") as fd:
                      for a in ann:
                          print(f"{a['id']} {a['cx']} {a['cy']} {a['bw']} {a['bh']}", file=fd);

             labels=[k["name"] for k in sorted(self._annotations["categories"],key=lambda x: x["id"])];
             with open(os.path.join(target,"dataset.yaml"),"wt",encoding="utf-8") as fd:
                  print(f"#path: {target}", file=fd);
                  print(f"train: ./train",  file=fd);
                  print(f"val: ./val",      file=fd);
                  print(f"test: ./test",    file=fd);
                  print( "",                file=fd);
                  print(f"names: {labels}", file=fd);
            
          if compress:
             zip_target=f"{target}.zip";
             with zipfile.ZipFile(zip_target, 'w', zipfile.ZIP_DEFLATED) as zipf:
                  longitud_ruta_base = len(os.path.dirname(target));
                  nombre_directorio_fuente = os.path.basename(target);
                  for raiz, _, archivos in os.walk(target):
                      for archivo in archivos:
                          ruta_completa = os.path.join(raiz, archivo);
                          nombre_archivo_zip = ruta_completa[longitud_ruta_base + 1:];
                          zipf.write(ruta_completa, nombre_archivo_zip);
             return zip_target;

          else:   
             return target;

#===============================================================================
def splitDict(criteria, **kwargs):
    """
    Divide (split) un diccionario según un criterio (criteria) en forma de lista de claves.
    Devuelve una tupla con dos diccionarios: aquellos key:value que cumplen los criterior y aquellos que no.
    """
    rt=({},{});
    for key in kwargs:
        if key in criteria: rt[0][key]=kwargs[key];
        else:               rt[1][key]=kwargs[key];
    return rt;    
    
#===============================================================================
def prettyPrintException(e, render=True):
    from IPython.display import display, HTML;
    from jinja2 import Template;

    exception_template="""
    <!DOCTYPE html>
    <html lang="es">
    <head>
    <meta charset="UTF-8">
    <title>Tabla Desplegable</title>
    <style>
      .xdropdown-content {
        display: none;
        padding: 5px;
        text-align: left;
      }
      
      .coding-font {
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
      }
    </style>
    <script>
      function toggleDropdown() { 
                var content = document.getElementById("dropdownContent");
                if (content.style.display === "block") { 
                    content.style.display = "none"; 
                   }
                else {
                    content.style.display = "block"; 
                   } 
               }
    </script>
    </head>
    <body>
    <table style="border-collapse: separate; border-spacing: 0; border-radius: 5px; background-color: #DC143C; color: white; width: 100%; border-collapse: collapse; margin-top:20px">
    
      <tr>
        <td style="width: 1px; white-space: nowrap; transform: rotate(-90deg); transform-origin: left botton; pading:10px 0; height: 100%; vertical-align: middle">        
          <b>Excepción</b>
        </td>
        <td>
          <table style="width: 100%;">
            <tr>         
              <td>
                 <p style="text-shadow: 2px 2px 2px black;"><b>Ha ocurrido una excepción:</b></p>
                 <p style="">{{message|e}}</p>
              </td>
            </tr>
            <tr>
              <td>
                <a onclick="toggleDropdown(); return false;" style="cursor:pointer; text-decoration: none; color:black">&#x25BC;</a>
                <div id="dropdownContent" class="dropdown-content" style="display: none; padding: 5px; text-align: left;">
                  <p style="color:LightGreen; text-shadow: 2px 2px 2px black;"><b>Trazado de la pila:</b></p>
                  {%for point in trace%}
                        <hr/>
                        <p style="background-color:#FAEBD7; color:black; padding: 5px">
                          <b style="">Fichero:</b> <b>{{point.filename|e}}</b> [en la línea <b>{{point.line|e}}</b>]<br/>
                          <b style="">Texto:</b> <span class="coding-font">{{point.text|e}}</span><br/>
                        </p>                    
                  {%endfor%}
                </div>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
    </body>
    </html>
    """

    import sys, traceback, linecache;
    exc_type, exc_value, exc_traceback = sys.exc_info();
    trace_list = traceback.extract_tb(exc_traceback);
    detailed_trace = [];
    for frame in trace_list:
        filename = frame.filename
        lineno = frame.lineno
        line_text = linecache.getline(filename, lineno).strip()
        detailed_trace.append({"filename":filename, "line":lineno, "text":line_text});

    gvars={ "message":str(e),
            "trace":detailed_trace,
          };
    template = Template(exception_template);
    html = template.render(**gvars);
    if render: display(HTML(html));
    return html;
    
    