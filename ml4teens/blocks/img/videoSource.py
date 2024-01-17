import sys, os, copy;
import time;
import cv2 as cv;
import numpy as np;
import PIL;
import requests;

from PIL.Image import Image;

from tempfile import NamedTemporaryFile;

from ...core import Block;

class VideoSource(Block):

      #-------------------------------------------------------------------------
      # speed:float [0,10]
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          self.sync=True;
          
          self._source=None;
          self._fuente=None;
          self._istemp=None;
          self._fd    =None;
          self._tm    =None;
          self._delay =None;
          
      #-------------------------------------------------------------------------
      def __del__(self):
          self.reset();

      #-------------------------------------------------------------------------
      def reset(self):
      
          if self._fd is not None:
             self._fd.release();
             
          if self._fuente is not None and self._istemp:
             os.remove(self._fuente);
             
          self._fd    =None;
          self._source=None;
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
      @Block.signal("source", str)
      def signal_source(self, data):
          return data;

      #-------------------------------------------------------------------------
      """
      @Block.signal("device", int)
      def signal_frame(self, frame):
          return frame;
      """
      
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

          # TODO 'fuente' puede ser un número de dispositivo! Y lo será.
          
          # TODO mandar la señal 'source'
          # TODO mandar la señal 'device'

          self.reset();
          
          self._source=source;
          
          if self._source.startswith("http"):
             with requests.get(self._source, stream=True) as r:
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
          try:
            if not self._fd.isOpened():
               raise RuntimeError(f"Error al abrir el vídeo '{self._fuente}'");
               
            else:
                ancho       = self._fd.get(cv.CAP_PROP_FRAME_WIDTH);
                alto        = self._fd.get(cv.CAP_PROP_FRAME_HEIGHT);
                fps         = self._fd.get(cv.CAP_PROP_FPS);
                frames      = self._fd.get(cv.CAP_PROP_FRAME_COUNT);
                codificador = int(self._fd.get(cv.CAP_PROP_FOURCC));
                
                self._delay = 1/fps;
                
                speed=self.params.speed or 1;
                self._delay=self._delay*speed;

                self.signal_info({"source":self._source, "width":ancho, "height":alto, "fps":fps, "frames":frames, "encoder":codificador, "delay":int(self._delay*1000) });

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

          try:
            if self._fd is None or not self._fd.isOpened():
               raise RuntimeError(f"Se ha invocado al slot 'next' de '{self._fullClassName}' sin tener una fuente abierta.");
               
            else:
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
