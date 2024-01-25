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
          self._queue=[];
          #color: de las líneas
          #width: de las líneas

      #-------------------------------------------------------------------------
      # SLOTS
      #-------------------------------------------------------------------------
      @Block.slot("image", {Image})
      def slot_image(self, slot, data):
      
          if self.params.clear:
             self._queue.clear();
             
          array=np.array(data.convert("RGB"));
          salida=data.copy();
          locations = fr.face_locations(array);
          imageDraw=PIL.ImageDraw.Draw(salida);
          rt=[];
          for loc in locations:
              top, right, bottom, left = loc;
              imageDraw.rectangle(((left, top, right, bottom)), fill=None, outline=(self.params.color or "red"), width=(self.params.width or 1));
              box={"kind":"face", "trust":1.0, "xyxy":(left/data.width, top/data.height, right/data.width, bottom/data.height)};
              self._queue.append(box);
              rt.append(box);
          try:
            self.signal_box(self._queue.pop(0));
          except IndexError:
            self.signal_box(None);
            
          self.signal_boxes(rt);
          self.signal_image(salida);

      #-------------------------------------------------------------------------
      @Block.slot("next", {object})
      def slot_next(self, slot, data):
          try:
            box=self._queue.pop(0);
            self.signal_box(box);
          except IndexError:
            self.signal_box(None);
          
      #-------------------------------------------------------------------------
      # SIGNALS
      #-------------------------------------------------------------------------
      @Block.signal("image", Image)
      def signal_image(self, data):
          return data;

      #-------------------------------------------------------------------------
      @Block.signal("box", dict)
      def signal_box(self, data):
          return data;
          
      #-------------------------------------------------------------------------
      @Block.signal("boxes", list)
      def signal_boxes(self, data):
          return data;
