import cv2 as cv;
import numpy as np;

#from PIL.Image import Image;
from PIL.Image import Image, fromarray;
#from PIL.Image import merge;

from ..core import Block;

class ConvertImage(Block):

      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);

      #-------------------------------------------------------------------------
      @Block.slot("1bit", {Image, np.ndarray}, required=3)
      def slot_1bit(self, slot, data):
          if isinstance(data,np.ndarray): self.signal_image(fromarray(data, mode='1'));
          else:                           self.signal_image(data.convert('1'));
          self.reset(slot);

      #-------------------------------------------------------------------------
      @Block.slot("L", {Image, np.ndarray}, required=4)
      def slot_L(self, slot, data):
          if isinstance(data,np.ndarray): self.signal_image(fromarray(data, mode='L'));
          else:                           self.signal_image(data.convert('L'));
          self.reset(slot);

      #-------------------------------------------------------------------------
      @Block.slot("LA", {Image, np.ndarray}, required=5)
      def slot_L(self, slot, data):
          if isinstance(data,np.ndarray): self.signal_image(fromarray(data, mode='LA'));
          else:                           self.signal_image(data.convert('LA'));
          self.reset(slot);

      #-------------------------------------------------------------------------
      @Block.slot("P", {Image, np.ndarray}, required=6)
      def slot_P(self, slot, data):
          if isinstance(data,np.ndarray): self.signal_image(fromarray(data, mode='P'));
          else:                           self.signal_image(data.convert('P'));
          self.reset(slot);

      #-------------------------------------------------------------------------
      @Block.slot("PA", {Image, np.ndarray}, required=7)
      def slot_P(self, slot, data):
          if isinstance(data,np.ndarray): self.signal_image(fromarray(data, mode='PA'));
          else:                           self.signal_image(data.convert('PA'));
          self.reset(slot);

      #-------------------------------------------------------------------------
      @Block.slot("RGB", {Image, np.ndarray}, required=8)
      def slot_rgb(self, slot, data):
          if isinstance(data,np.ndarray): self.signal_image(fromarray(data, mode="RGB"));
          else:                           self.signal_image(data.convert('RGB'));
          self.reset(slot);

      #-------------------------------------------------------------------------
      @Block.slot("RGBA", {Image, np.ndarray}, required=9)
      def slot_rgba(self, slot, data):
          if isinstance(data,np.ndarray): self.signal_image(fromarray(data, mode="RGBA"));
          else:                           self.signal_image(data.convert('RGBA'));
          self.reset(slot);

      #-------------------------------------------------------------------------
      @Block.slot("CMYK", {Image, np.ndarray}, required=10)
      def slot_cmyk(self, slot, data):
          if isinstance(data,np.ndarray): self.signal_image(fromarray(data, mode="CMYK"));
          else:                           self.signal_image(data.convert('CMYK'));
          self.reset(slot);

      #-------------------------------------------------------------------------
      @Block.slot("YCbCr", {Image, np.ndarray}, required=11)
      def slot_ycbcr(self, slot, data):
          if isinstance(data,np.ndarray): self.signal_image(fromarray(data, mode="YCbCr"));
          else:                           self.signal_image(data.convert('YCbCr'));
          self.reset(slot);

      #-------------------------------------------------------------------------
      @Block.slot("LAB", {Image, np.ndarray}, required=12)
      def slot_lab(self, slot, data):
          if isinstance(data,np.ndarray): self.signal_image(fromarray(data, mode="LAB"));
          else:                           self.signal_image(data.convert('LAB'));
          self.reset(slot);

      #-------------------------------------------------------------------------
      @Block.slot("HSV", {Image, np.ndarray}, required=13)
      def slot_hsv(self, slot, data):
          if isinstance(data,np.ndarray): self.signal_image(fromarray(data, mode="HSV"));
          else:                           self.signal_image(data.convert('HSV'));
          self.reset(slot);

      #-------------------------------------------------------------------------
      @Block.slot("I", {Image, np.ndarray}, required=14)
      def slot_I(self, slot, data):
          if isinstance(data,np.ndarray): self.signal_image(fromarray(data, mode="I"));
          else:                           self.signal_image(data.convert('I'));
          self.reset(slot);

      #-------------------------------------------------------------------------
      @Block.slot("F", {Image, np.ndarray}, required=15)
      def slot_F(self, slot, data):
          if isinstance(data,np.ndarray): self.signal_image(fromarray(data, mode="F"));
          else:                           self.signal_image(data.convert('F'));
          self.reset(slot);

      #-------------------------------------------------------------------------
      @Block.signal("image", Image)
      def signal_image(self, data):
          return data;

      #-------------------------------------------------------------------------
      def run(self, **kwarg):
          raise RuntimeError("No tiene sentido invocar el método 'run' de un objeto de clase 'ConvertImage'.");
