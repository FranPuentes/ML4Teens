import sys, os;
import time;
import cv2 as cv;
import numpy as np;

import requests;
from tempfile import NamedTemporaryFile;

from ..core import Block;

class VideoSource(Block):

      #-------------------------------------------------------------------------
      # fuente
      def __init__(self, **kwargs):
          super().__init__(**kwargs);

      #-------------------------------------------------------------------------
      @Block.signal("frame", np.ndarray)
      def signal_frame(self, frame):
          return frame;

      #-------------------------------------------------------------------------
      @Block.signal("dimensiones", tuple)
      def signal_dimensiones(self, data):
          return data;

      #-------------------------------------------------------------------------
      @Block.signal("información", dict)
      def signal_información(self, data):
          return data;

      #-------------------------------------------------------------------------
      def run(self, **kwargs):
          if kwargs and "fuente" in kwargs: fuente = kwargs     ["fuente"];
          else:                             fuente = self._param("fuente");

          if not fuente or type(fuente) is not str: raise RuntimeError(f"Necesito que pases como parámetro 'fuente' el nombre del fichero o la url que contiene el vídeo.");

          istemp=False;
          if type(fuente) is str and fuente.startswith("http"):
             with requests.get(fuente, stream=True) as r:
                  r.raise_for_status();
                  with NamedTemporaryFile(delete=False, suffix='.mp4') as f:
                       for chunk in r.iter_content(chunk_size=65536//4):
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

                self.signal_información({"fuente":fuente, "ancho":ancho, "alto":alto, "fps":fps, "frames":frames, "codificador":codificador, "delay":delay });

                ok, frame = fd.read();
                if ok:
                   if len(frame.shape) == 3: shape=(alto,ancho,frame.shape[2]);
                   else:                     shape=(alto,ancho,1);
                   self.signal_dimensiones(shape);

                   while ok:
                         timestamp=time.time();

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
