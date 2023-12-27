import IPython;
from IPython.display import update_display;
from io import BytesIO;
import numpy as np;

from ..core import Block;

class Screen(Block):

      #-------------------------------------------------------------------------
      # width
      # height
      def __init__(self, *args, **kwargs):
          super().__init__(*args, **kwargs);

      #-------------------------------------------------------------------------
      @Block.signal("imagen", IPython.display.Image)
      def signal_imagen(self, data):
          return data;

      #-------------------------------------------------------------------------
      @Block.signal("frame", np.ndarray)
      def signal_frame(self, data):
          return data;

      #-------------------------------------------------------------------------
      def _redim(self, imagen, width=None, height=None):
          if width is None and height is None: return imagen;
          (h, w) = imagen.shape[:2];
          if width is None:
             r = height / float(h);
             dimensiones = (int(w * r), height);
          else:
             r = width / float(w);
             dimensiones = (width, int(h * r));
          imagen = cv.resize(imagen, dimensiones, interpolation=cv.INTER_AREA);
          return imagen;

      #-------------------------------------------------------------------------
      @Block.slot("imagen", {IPython.display.Image}, required=2)
      def slot_image(self, slot, imagen):
          width =self._param("width", None);
          height=self._param("height",None);
          imagen=self._redim(imagen,width,height);
          update_display(imagen, display_id=self._id);
          self.signal_imagen(imagen);
          self.reset("imagen");

      #-------------------------------------------------------------------------
      @Block.slot("frame", {np.ndarray}, required=2)
      def slot_frame(self, slot, frame):
          width =self._param("width", None);
          height=self._param("height",None);
          frame=self._redim(frame,width,height);
          _, buffer = cv.imencode('.png', frame);
          buffer = BytesIO(buffer);
          imagen=IPython.display.Image(data=buffer.read(), format='png');
          update_display(imagen, display_id=self._id);
          self.signal_imagen(imagen);
          self.reset("frame");

      #-------------------------------------------------------------------------
      def run(self, **kwarg):
          raise RuntimeError("No tiene sentido invocar el método 'run' de un objeto de clase 'Pantalla'.");
          