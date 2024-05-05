# -*- coding: utf-8 -*-

import sys, os, copy;
import time;
import cv2 as cv;
import numpy as np;
import PIL;
import requests;

from PIL.Image import Image;

from tempfile import NamedTemporaryFile;

from ...core import Block;

################################################################################
class VideoSourceNoSync(Block):

      #-------------------------------------------------------------------------
      # speed:float [0,10]
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          
          self._source=None;
          self._device=None;
          self._fuente=None;
          self._istemp=None;
          self._fd    =None;
          self._tm    =None;
          self._delay =None;
          
      #-------------------------------------------------------------------------
      def close(self):
          self.reset();
          
      #-------------------------------------------------------------------------
      def reset(self):
      
          if self._fd is not None:
             self._fd.release();
             
          if self._fuente is not None and self._istemp:
             os.remove(self._fuente);
             
          self._fd    =None;
          self._source=None;
          self._device=None;
          self._fuente=None;
          self._istemp=None;
          self._tm    =None;
          self._delay =None;                       

      #-------------------------------------------------------------------------
      def _resize(self, imagen, width, height):
      
          _width, _height = imagen.size;

          if width is None and height is None : return imagen;

          if width==_width and height==_height and not self.params.box: return imagen;
          
          if height is None:
              ratio  = _width / width;
              height = int(_height / ratio);

          elif width is None:
              ratio = _height / height;
              width = int(_width / ratio);
          
          # https://pillow.readthedocs.io/en/latest/handbook/concepts.html#filters
          
          # TODO (x,y,w,h) puede ser relativo a tamaño de la imagen
          
          box=self.params.box; # (x,y,w,h)
          
          if self.params.filter:
             if self.params.filter.upper()=="NEAREST":  return imagen.resize((width, height), PIL.Image.Resampling.NEAREST, box);
             if self.params.filter.upper()=="BOX":      return imagen.resize((width, height), PIL.Image.Resampling.BOX,     box);
             if self.params.filter.upper()=="BILINEAR": return imagen.resize((width, height), PIL.Image.Resampling.BILINEAR,box);
             if self.params.filter.upper()=="HAMMING":  return imagen.resize((width, height), PIL.Image.Resampling.HAMMING, box);
             if self.params.filter.upper()=="BICUBIC":  return imagen.resize((width, height), PIL.Image.Resampling.BICUBIC, box);
             if self.params.filter.upper()=="LANCZOS":  return imagen.resize((width, height), PIL.Image.Resampling.LANCZOS, box);
             
          return imagen.resize((width, height));
          
      #-------------------------------------------------------------------------
      #@Block.signal("source", str)
      #def signal_source(self, data):
      #    return data;

      #-------------------------------------------------------------------------
      @Block.signal("frame", Image)
      def signal_frame(self, frame):
          return frame;

      #-------------------------------------------------------------------------
      @Block.signal("dims", tuple)
      def signal_dims(self, data):
          return data;

      #-------------------------------------------------------------------------
      @Block.signal("info", dict)
      def signal_info(self, data):
          return data;

      #-------------------------------------------------------------------------
      @Block.signal("begin", int)
      def signal_begin(self, data):
          return data;

      #-------------------------------------------------------------------------
      @Block.signal("end", bool)
      def signal_end(self, data):
          return data;
                     
      #-------------------------------------------------------------------------
      @Block.slot("source", {str,int})
      def slot_source(self, slot, source):

          self.reset();
          
          if type(source) is str:
          
             self._source=source;
             self._device=None;
             
             if self._source.startswith("http"):
                headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0' }
                with requests.get(self._source, stream=True, headers=headers) as r:
                     r.raise_for_status();
                     with NamedTemporaryFile(delete=False, suffix='.mp4') as f:
                          for chunk in r.iter_content(chunk_size=65536//8):
                              f.write(chunk);
                          self._fuente = f.name;
                          self._istemp = True;
             else:
                self._fuente = self._source;
                self._istemp = False;

             if not os.path.exists(self._fuente): raise RuntimeError(f"El fichero '{self._fuente}', no existe.");

             self._fd = cv.VideoCapture(self._fuente);
             
          elif type(source) is int:
             
             self._source=None;
             self._device=source;
             
             self._fd = cv.VideoCapture(self._device);
             
             if self.params.closeButton:
                text="Cerrar Webcam";
                if self.params.closeButton is str and len(self.params.closeButton)>0:
                   text=self.params.closeButton;
                import ipywidgets as widgets;
                from IPython.display import display;
                button = widgets.Button(description=text);
                button.style.button_color = 'lightgreen';  # Cambiar el color de fondo del botón
                button.style.font_weight = 'bold';         # Cambiar el peso de la fuente a negrita
                button.layout.width = '200px';             # Cambiar el ancho del botón
                button.layout.height = '40px';             # Cambiar la altura del botón
                button.layout.border = '2px solid black';  # Agregar un borde al botón
                button.on_click(lambda _: self.close());
                display(button);
          
          try:
            if self._fd is None or not self._fd.isOpened():
               raise RuntimeError(f"Error al abrir el vídeo '{source}'");
               
            else:
               ancho       = self._fd.get(cv.CAP_PROP_FRAME_WIDTH);
               alto        = self._fd.get(cv.CAP_PROP_FRAME_HEIGHT);
               fps         = self._fd.get(cv.CAP_PROP_FPS);
               frames      = self._fd.get(cv.CAP_PROP_FRAME_COUNT);
               codificador = int(self._fd.get(cv.CAP_PROP_FOURCC));
                
               self._delay = 1/fps;
                
               speed=self.params.speed or 1;
               self._delay=self._delay*speed;

               self.signal_info({"source":self._source or self._device, 
                                 "width":ancho, 
                                 "height":alto, 
                                 "fps":fps, 
                                 "frames":frames, 
                                 "encoder":codificador, 
                                 "delay":int(self._delay*1000) });

               ok, frame = self._fd.read();
                
               if not ok:
                  self.signal_end(True);
                  self.reset();
                
               else:
                  assert len(frame.shape)==2 or (len(frame.shape)==3 and frame.shape[2] in [3, 4]), "Formato de vídeo no soportado";

                  self.signal_begin(frames);
                
                  if len(frame.shape)==3: shape=(alto,ancho,frame.shape[2]);
                  else:                   shape=(alto,ancho,1);
                  self.signal_dims(shape);
                   
                  self._tm = time.time();

                  # TODO, quedarnos sólo con unos pocos modos: L, RGB, RGBA, ...
                   
                  if len(frame.shape)==2:
                     frame=frame;
                  else:
                     if frame.shape[2]==3:
                        frame=cv.cvtColor(frame, cv.COLOR_BGR2RGB);
                     else:
                        frame=cv.cvtColor(frame, cv.COLOR_BGRA2RGBA);
                             
                  frame = PIL.Image.fromarray(frame);
                  frame = self._resize(frame, self.params.width, self.params.height);
                  self.signal_frame(frame);
                   
          except Exception as e:
            self.signal_end(False);
            self.reset();
            raise e;
            
      #-------------------------------------------------------------------------
      @Block.slot("next", {object})
      def slot_next(self, slot, _):

          if self._fd is None or not self._fd.isOpened():
             self.reset();
             return;
             
          try:
            ok, frame = self._fd.read();
            
            if not ok:
               self.signal_end(True);
               self.reset();
           
            else:
               assert len(frame.shape)==2 or (len(frame.shape)==3 and frame.shape[2] in [3, 4]), "Formato de vídeo no soportado";
           
               diff=(time.time()-self._tm);
               if diff>=self._delay: pass;
               else:                 time.sleep(self._delay-diff);

               self._tm = time.time();
              
               # TODO, quedarnos sólo con unos pocos modos: L, RGB, RGBA, ...
              
               if len(frame.shape)==2:
                  frame=frame;
               else:
                  if frame.shape[2]==3:
                     frame=cv.cvtColor(frame, cv.COLOR_BGR2RGB);
                  else:
                     frame=cv.cvtColor(frame, cv.COLOR_BGRA2RGBA);
                        
               frame = PIL.Image.fromarray(frame);
               frame = self._resize(frame, self.params.width, self.params.height);
               self.signal_frame(frame);
                      
          except Exception as e:
            self.signal_end(False);
            self.reset();
            raise e;

      #-------------------------------------------------------------------------
      @Block.slot("close", {object})
      def slot_close(self, slot, _):
          self.reset();

################################################################################          
class VideoSource(Block):

      #-------------------------------------------------------------------------
      # speed:float [0,10]
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          
          self._source=None;
          self._device=None;
          self._fuente=None;
          self._istemp=None;
          self._fd    =None;
          self._tm    =None;
          self._delay =None;
          
      #-------------------------------------------------------------------------
      def close(self):
          self.reset();
          
      #-------------------------------------------------------------------------
      def reset(self):
      
          if self._fd is not None:
             self._fd.release();
             
          if self._fuente is not None and self._istemp:
             os.remove(self._fuente);
             
          self._fd    =None;
          self._source=None;
          self._device=None;
          self._fuente=None;
          self._istemp=None;
          self._tm    =None;
          self._delay =None;                       

      #-------------------------------------------------------------------------
      def _resize(self, imagen, width, height):
      
          _width, _height = imagen.size;

          if width is None and height is None : return imagen;

          if width==_width and height==_height and not self.params.box: return imagen;
          
          if height is None:
              ratio  = _width / width;
              height = int(_height / ratio);

          elif width is None:
              ratio = _height / height;
              width = int(_width / ratio);
          
          # https://pillow.readthedocs.io/en/latest/handbook/concepts.html#filters
          
          # TODO (x,y,w,h) puede ser relativo a tamaño de la imagen
          
          box=self.params.box; # (x,y,w,h)
          
          if self.params.filter:
             if self.params.filter.upper()=="NEAREST":  return imagen.resize((width, height), PIL.Image.Resampling.NEAREST, box);
             if self.params.filter.upper()=="BOX":      return imagen.resize((width, height), PIL.Image.Resampling.BOX,     box);
             if self.params.filter.upper()=="BILINEAR": return imagen.resize((width, height), PIL.Image.Resampling.BILINEAR,box);
             if self.params.filter.upper()=="HAMMING":  return imagen.resize((width, height), PIL.Image.Resampling.HAMMING, box);
             if self.params.filter.upper()=="BICUBIC":  return imagen.resize((width, height), PIL.Image.Resampling.BICUBIC, box);
             if self.params.filter.upper()=="LANCZOS":  return imagen.resize((width, height), PIL.Image.Resampling.LANCZOS, box);
             
          return imagen.resize((width, height));
          
      #-------------------------------------------------------------------------
      #@Block.signal("source", str)
      #def signal_source(self, data):
      #    return data;

      #-------------------------------------------------------------------------
      @Block.signal("frame", Image, sync=True)
      def signal_frame(self, frame):
          return frame;

      #-------------------------------------------------------------------------
      @Block.signal("dims", tuple)
      def signal_dims(self, data):
          return data;

      #-------------------------------------------------------------------------
      @Block.signal("info", dict)
      def signal_info(self, data):
          return data;

      #-------------------------------------------------------------------------
      @Block.signal("begin", int, sync=True)
      def signal_begin(self, data):
          return data;

      #-------------------------------------------------------------------------
      @Block.signal("end", bool, sync=True)
      def signal_end(self, data):
          return data;
                     
      #-------------------------------------------------------------------------
      @Block.slot("source", {str,int})
      def slot_source(self, slot, source):

          self.reset();
          
          if type(source) is str:
          
             self._source=source;
             self._device=None;
             
             if self._source.startswith("http"):
                headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0' }
                with requests.get(self._source, stream=True, headers=headers) as r:
                     r.raise_for_status();
                     with NamedTemporaryFile(delete=False, suffix='.mp4') as f:
                          for chunk in r.iter_content(chunk_size=65536//8):
                              f.write(chunk);
                          self._fuente = f.name;
                          self._istemp = True;
             else:
                self._fuente = self._source;
                self._istemp = False;

             if not os.path.exists(self._fuente): raise RuntimeError(f"El fichero '{self._fuente}', no existe.");

             self._fd = cv.VideoCapture(self._fuente);
             
          elif type(source) is int:
             
             self._source=None;
             self._device=source;
             
             self._fd = cv.VideoCapture(self._device);
             
             if self.params.closeButton:
                text="Cerrar Webcam";
                if self.params.closeButton is str and len(self.params.closeButton)>0:
                   text=self.params.closeButton;
                import ipywidgets as widgets;
                from IPython.display import display;
                button = widgets.Button(description=text);
                button.style.button_color = 'lightgreen';  # Cambiar el color de fondo del botón
                button.style.font_weight = 'bold';         # Cambiar el peso de la fuente a negrita
                button.layout.width = '200px';             # Cambiar el ancho del botón
                button.layout.height = '40px';             # Cambiar la altura del botón
                button.layout.border = '2px solid black';  # Agregar un borde al botón
                button.on_click(lambda _: self.close());
                display(button);
          
          try:
            if self._fd is None or not self._fd.isOpened():
               raise RuntimeError(f"Error al abrir el vídeo '{source}'");
               
            else:
               ancho       = self._fd.get(cv.CAP_PROP_FRAME_WIDTH);
               alto        = self._fd.get(cv.CAP_PROP_FRAME_HEIGHT);
               fps         = self._fd.get(cv.CAP_PROP_FPS);
               frames      = self._fd.get(cv.CAP_PROP_FRAME_COUNT);
               codificador = int(self._fd.get(cv.CAP_PROP_FOURCC));
                
               self._delay = 1/fps;
                
               speed=self.params.speed or 1;
               self._delay=self._delay*speed;

               self.signal_info({"source":self._source or self._device, 
                                 "width":ancho, 
                                 "height":alto, 
                                 "fps":fps, 
                                 "frames":frames, 
                                 "encoder":codificador, 
                                 "delay":int(self._delay*1000) });

               ok, frame = self._fd.read();              
               
               self.signal_begin(frames);
               
               while ok: 
                      
                     assert len(frame.shape)==2 or (len(frame.shape)==3 and frame.shape[2] in [3, 4]), "Formato de vídeo no soportado";

                   
                     if len(frame.shape)==3: shape=(alto,ancho,frame.shape[2]);
                     else:                   shape=(alto,ancho,1);
                     self.signal_dims(shape);
                      
                     self._tm = time.time();

                     # TODO, quedarnos sólo con unos pocos modos: L, RGB, RGBA, ...
                      
                     if len(frame.shape)==2:
                        frame=frame;
                     else:
                        if frame.shape[2]==3:
                           frame=cv.cvtColor(frame, cv.COLOR_BGR2RGB);
                        else:
                           frame=cv.cvtColor(frame, cv.COLOR_BGRA2RGBA);
                                
                     frame = PIL.Image.fromarray(frame);
                     frame = self._resize(frame, self.params.width, self.params.height);
                     self.signal_frame(frame);
                     
                     try:
                       ok, frame = self._fd.read();
                     except Exception:
                       break;  
                   
               self.signal_end(True);
            
          except Exception as e:
            self.signal_end(False);
            raise e;
            
          finally:  
            self.reset();
            
