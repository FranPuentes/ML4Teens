import numpy as np;
import PIL;

from PIL.Image import Image;

# https://github.com/ageitgey/face_recognition

import face_recognition as fr;

from ...core import Block;

#===============================================================================
class FaceBoxing(Block):

      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          #color: de las líneas
          #width: de las líneas

      #-------------------------------------------------------------------------
      # SLOTS
      #-------------------------------------------------------------------------
      @Block.slot("image", {Image})
      def slot_image(self, slot, data):
          array=np.array(data.convert("RGB"));
          salida=data.copy();
          locations = fr.face_locations(array);
          imageDraw=PIL.ImageDraw.Draw(salida);
          boxes=[];
          for loc in locations:
              top, right, bottom, left = loc;
              imageDraw.rectangle(((left, top, right, bottom)), fill=None, outline=(self.params.color or "red"), width=(self.params.width or 1));
              boxes.append({"kind":"face", "trust":1.0, "xyxy":(left/data.width, top/data.height, right/data.width, bottom/data.height)});
          self.signal_boxes(boxes);
          self.signal_image(salida);

     #-------------------------------------------------------------------------
      # SIGNALS
      #-------------------------------------------------------------------------
      @Block.signal("image", Image)
      def signal_image(self, data):
          return data;

      #-------------------------------------------------------------------------
      @Block.signal("boxes", list)
      def signal_boxes(self, data):
          return data;
