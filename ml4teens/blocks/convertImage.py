import cv2 as cv;
import numpy as np;

from PIL.Image import Image;

from ..core import Block;

class ConvertImage(Block):

      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);

      #-------------------------------------------------------------------------
      @Block.slot("1bit", {Image})
      def slot_1bit(self, slot, data):
          self.signal_image(data.convert('1'));

      #-------------------------------------------------------------------------
      @Block.slot("L", {Image})
      def slot_L(self, slot, data):
          self.signal_image(data.convert('L'));

      #-------------------------------------------------------------------------
      @Block.slot("LA", {Image})
      def slot_L(self, slot, data):
          self.signal_image(data.convert('LA'));

      #-------------------------------------------------------------------------
      @Block.slot("P", {Image})
      def slot_P(self, slot, data):
          self.signal_image(data.convert('P'));

      #-------------------------------------------------------------------------
      @Block.slot("PA", {Image})
      def slot_P(self, slot, data):
          self.signal_image(data.convert('PA'));

      #-------------------------------------------------------------------------
      @Block.slot("RGB", {Image})
      def slot_rgb(self, slot, data):
          self.signal_image(data.convert('RGB'));

      #-------------------------------------------------------------------------
      @Block.slot("RGBA", {Image})
      def slot_rgba(self, slot, data):
          self.signal_image(data.convert('RGBA'));

      #-------------------------------------------------------------------------
      @Block.slot("CMYK", {Image})
      def slot_cmyk(self, slot, data):
          self.signal_image(data.convert('CMYK'));

      #-------------------------------------------------------------------------
      @Block.slot("YCbCr", {Image})
      def slot_ycbcr(self, slot, data):
          self.signal_image(data.convert('YCbCr'));

      #-------------------------------------------------------------------------
      @Block.slot("LAB", {Image})
      def slot_lab(self, slot, data):
          self.signal_image(data.convert('LAB'));

      #-------------------------------------------------------------------------
      @Block.slot("HSV", {Image})
      def slot_hsv(self, slot, data):
          self.signal_image(data.convert('HSV'));

      #-------------------------------------------------------------------------
      @Block.slot("I", {Image})
      def slot_I(self, slot, data):
          self.signal_image(data.convert('I'));

      #-------------------------------------------------------------------------
      @Block.slot("F", {Image})
      def slot_F(self, slot, data):
          self.signal_image(data.convert('F'));

      #-------------------------------------------------------------------------
      @Block.signal("image", Image)
      def signal_image(self, data):
          return data;
