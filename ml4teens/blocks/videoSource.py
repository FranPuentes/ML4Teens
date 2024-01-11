import sys, os, copy;
import time;
import cv2 as cv;
import numpy as np;
import PIL;
import requests;

from PIL.Image import Image;

from tempfile import NamedTemporaryFile;

from ..core import Context;
from ..core import Block;

class VideoSource(Block):

      #-------------------------------------------------------------------------
      # speed:float [0,10]
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          self.sync=True;

      #-------------------------------------------------------------------------
      @Block.signal("source", str)
      def signal_frame(self, frame):
          return frame;

      #-------------------------------------------------------------------------
      @Block.signal("device", int)
      def signal_frame(self, frame):
          return frame;

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
      @Block.slot("source", {str,int})
      def slot_source(self, slot, fuente):

          # TODO 'fuente' puede ser un número de dispositivo! Y lo será.
          
          # TODO mandar la señal 'source'
          # TODO mandar la señal 'device'

          istemp=False;
          if fuente.startswith("http"):
             with requests.get(fuente, stream=True) as r:
                  r.raise_for_status();
                  with NamedTemporaryFile(delete=False, suffix='.mp4') as f:
                       for chunk in r.iter_content(chunk_size=65536//8):
                           f.write(chunk);
                       fuente = f.name;
                       istemp=True;

          if not os.path.exists(fuente): raise RuntimeError(f"El fichero '{fuente}', no existe.");

          fd = cv.VideoCapture(fuente);
          try:
            if not fd.isOpened(): raise RuntimeError(f"Error al abrir el vídeo '{fuente}'");
            else:
                ancho       = fd.get(cv.CAP_PROP_FRAME_WIDTH);
                alto        = fd.get(cv.CAP_PROP_FRAME_HEIGHT);
                fps         = fd.get(cv.CAP_PROP_FPS);
                frames      = fd.get(cv.CAP_PROP_FRAME_COUNT);
                codificador = int(fd.get(cv.CAP_PROP_FOURCC));
                delay       = int(1000/fps);
                
                speed=self.params.speed or 1;
                delay=delay*speed;

                self.signal_info({"source":fuente, "width":ancho, "height":alto, "fps":fps, "frames":frames, "encoder":codificador, "delay":delay });

                ok, frame = fd.read();
                
                assert len(frame.shape)==2 or (len(frame.shape)==3 and frame.shape[2] in [3, 4]), "Formato de vídeo no soportado";
                
                if ok:
                   if len(frame.shape)==3: shape=(alto,ancho,frame.shape[2]);
                   else:                   shape=(alto,ancho,1);
                   self.signal_dims(shape);

                   self.signal_begin(frames);
                   
                   while ok:
                         timestamp=time.time();

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
                         
                         ok, frame = fd.read();

                         diff=int((time.time()-timestamp)*1000);
                         if diff>=delay: pass;
                         else:           time.sleep((delay-diff)/1000);
                         
                   self.signal_end(True);
                   
          except Exception as e:
            self.signal_end(False);
            raise e;
            
          finally:
            fd.release();
            if istemp: os.remove(fuente);
            del self.tokens["source"];

