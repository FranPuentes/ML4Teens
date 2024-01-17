import numpy as np;
import PIL;

from PIL.Image import Image;

# https://github.com/ageitgey/face_recognition

import face_recognition as fr;

from ...core import Block;

#===============================================================================
class FaceLandmarks(Block):

      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          #color: de los puntos
          #width: de los puntos

      #-------------------------------------------------------------------------
      # SLOTS
      #-------------------------------------------------------------------------
      @Block.slot("image", {Image})
      def slot_image(self, slot, data):
          array=np.array(data.convert("RGB"));
          salida=data.copy();
          landmarks = fr.face_landmarks(array);
          imageDraw=PIL.ImageDraw.Draw(salida);
          points=[];
          for landmark in landmarks:
              lnd=[];
              for key in landmark:
                  for x,y in landmark[key]: imageDraw.ellipse((x-1, y-1, x+1, y+1), fill=(self.params.color or 'red'), width=(self.params.width or 1));
                  lnd.append({"kind":f"face:{key}", "trust":1.0, "xy":[(x/data.width,y/data.height) for x,y in landmark[key]]});
              points.append(lnd);
          self.signal_landmarks(points);
          self.signal_image(salida);

     #-------------------------------------------------------------------------
      # SIGNALS
      #-------------------------------------------------------------------------
      @Block.signal("image", Image)
      def signal_image(self, data):
          return data;

      #-------------------------------------------------------------------------
      @Block.signal("landmarks", list)
      def signal_landmarks(self, data):
          return data;
