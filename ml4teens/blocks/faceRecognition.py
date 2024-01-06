import PIL;

from PIL.Image import Image;

# https://github.com/ageitgey/face_recognition
import face_recognition as fr;

from ..core import Block;

class FaceRecognition(Block):

      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__();

      #-------------------------------------------------------------------------
      # SLOTS
      #-------------------------------------------------------------------------
      @Block.slot("image", {Image}, required=2)
      def slot_image(self, slot, data):
          #locations = fr.face_locations(data);
          #landmarks = fr.face_landmarks(data);
          pass;


      #-------------------------------------------------------------------------
      # SIGNALS
      #-------------------------------------------------------------------------
      @Block.signal("image", Image)
      def signal_image(self, data):
          return data;

      #-------------------------------------------------------------------------
      @Block.signal("boxes", list)
      def signal_boxes(self, data):
          pass;

      #-------------------------------------------------------------------------
      @Block.signal("landmarks", list)
      def signal_landmarks(self, data):
          pass;
