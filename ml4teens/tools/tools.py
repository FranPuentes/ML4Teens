# -*- coding: utf-8 -*-
import sys, os, io;
import fnmatch;
from PIL import Image;
import requests;
from io import BytesIO;
import tempfile;

import glob;
import json;
import shutil;
import zipfile;

from itertools import accumulate;

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
    
    
    
    