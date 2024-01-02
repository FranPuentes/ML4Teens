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
      # source:str
      # speed:float TODO
      def __init__(self, **kwargs):
          super().__init__(**kwargs);          

      #-------------------------------------------------------------------------
      @Block.signal("frame", Image)
      def signal_frame(self, frame):
          return frame;

      #-------------------------------------------------------------------------
      @Block.signal("frames", int)
      def signal_frames(self, frame):
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
      @Block.slot("source", {str}, required=True)
      def slot_source(self, slot, fuente):

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

          min_diff=float("+inf");
          max_diff=float("-inf");
          
          fd = cv.VideoCapture(fuente);
          try:
            if not fd.isOpened(): raise RuntimeError(f"Error al abrir el vídeo '{fuente}'");
            else:
                ancho = fd.get(cv.CAP_PROP_FRAME_WIDTH);
                alto = fd.get(cv.CAP_PROP_FRAME_HEIGHT);
                fps = fd.get(cv.CAP_PROP_FPS);
                frames = fd.get(cv.CAP_PROP_FRAME_COUNT);
                codificador = int(fd.get(cv.CAP_PROP_FOURCC));
                delay = int(1000/fps);

                self.signal_frames(frames);
                self.signal_info({"fuente":fuente, "ancho":ancho, "alto":alto, "fps":fps, "frames":frames, "codificador":codificador, "delay":delay });

                ok, frame = fd.read();
                
                assert len(frame.shape)==2 or (len(frame.shape)==3 and frame.shape[2] in [3, 4]), "Formato de vídeo no soportado";
                
                if ok:
                   if len(frame.shape)==3: shape=(alto,ancho,frame.shape[2]);
                   else:                   shape=(alto,ancho,1);
                   self.signal_dims(shape);

                   while ok:
                         timestamp=time.time();

                         if len(frame.shape)==2:
                            frame=frame;
                         else:
                            if frame.shape[2]==3:
                               frame=cv.cvtColor(frame, cv.COLOR_BGR2RGB);
                            else:
                               frame=cv.cvtColor(frame, cv.COLOR_BGRA2RGBA);
                                   
                         frame = PIL.Image.fromarray(frame);
                         self.signal_frame(frame);
                         
                         ok, frame = fd.read();

                         diff=int((time.time()-timestamp)*1000);
                         min_diff=min(min_diff, diff);
                         max_diff=max(max_diff, diff);
                         if diff>=delay: pass;
                         else:           time.sleep((delay-diff)/1000);
          finally:
            fd.release();
            if istemp: os.remove(fuente);
      
      #-------------------------------------------------------------------------
      # source
      def run(self, **kwargs):
      
          old_params = copy.deepcopy(self._params);

          for key in kwargs:
              self._params[key]=kwargs[key];
          
          fuente=self._param("source");

          if not fuente or type(fuente) is not str:
             raise RuntimeError(f"Necesito que pases como parámetro 'source' el nombre del fichero o la url que contiene el vídeo.");

          try:
             Context.instance.accept(self, "source", fuente);
             
          finally:
             self._params=old_params;
                
             