from ultralytics import YOLO;
from PIL import Image;

import numpy as np;

from ..core import Block;

class ObjectID(Block):
      """
      Este bloque recibe una imagen (slot 'frame') en forma de tensor numpy, y emite la misma imagen, pero con elementos identificados.
      """

      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          model_name="yolov8n.pt";
          if "model" in kwargs: model_name=kwargs["model"];
          self._model = YOLO(model_name);

      #-------------------------------------------------------------------------
      @Block.slot("frame", {np.ndarray}, required=True)
      def slot_frame(self, slot, data):
          results = self._model(data, stream=True, verbose=False);
          for r in results:
              frame = r.plot();
              self.signal_frame(frame);
          self.reset("frame");

      #-------------------------------------------------------------------------
      @Block.signal("frame", np.ndarray)
      def signal_frame(self, data):
          return data;

      #-------------------------------------------------------------------------
      def run(self, **kwarg):
          raise RuntimeError("No tiene sentido invocar el método 'run' de un objeto de clase 'YOLO'.");
          