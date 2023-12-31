import cv2 as cv;

from PIL.Image import Image;
from PIL.Image import fromarray;

from ..core import Block;

class SingleChannel(Block):

      #-------------------------------------------------------------------------
      # channel
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          if "channel" in kwargs: self._channel=kwargs["channel"];
          else:                   self._channel=0;
          assert type(self._channel)==int, f"El parámetro 'channel' debe ser el número del canal (0, ...)";

      #-------------------------------------------------------------------------
      @Block.slot("image", {Image}, required=2)
      def slot_image(self, slot, data):
          assert type(data) is Image;
          c=len(data.getbands());
          n=self._channel;
          assert n in range(0,c), f"El canal {n} no puede ser extraído de una imagen de {c} canales (recuerda: empieza a contar en 0)";
          imagen=data.getchannel(n);
          self.signal_image(imagen);
          self.reset("image");

      #-------------------------------------------------------------------------
      @Block.signal("image", Image)
      def signal_image(self, data):
          return data;

      #-------------------------------------------------------------------------
      def run(self, **kwarg):
          raise RuntimeError("No tiene sentido invocar el método 'run' de un objeto de clase 'SingleChannel'.");
          