import cv2 as cv;
import numpy as np;

from ..core import Block;

class BlackAndWhite(Block):

      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);

      #-------------------------------------------------------------------------
      @Block.slot("frame", {np.ndarray}, required=True)
      def slot_frame(self, slot, data):
          frame = cv.cvtColor(data, cv.COLOR_BGR2GRAY);
          self.signal_frame(frame);
          self.reset("frame");

      #-------------------------------------------------------------------------
      @Block.signal("frame", np.ndarray)
      def signal_frame(self, data):
          return data;

      #-------------------------------------------------------------------------
      def run(self, **kwarg):
          raise RuntimeError("No tiene sentido invocar el método 'run' de un objeto de clase 'BlackAndWite'.");
