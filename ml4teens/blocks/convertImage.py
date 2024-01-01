import cv2 as cv;
import numpy as np;

from PIL.Image import Image;

from ..core import Block;

class ConvertImage(Block):

      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);

      #-------------------------------------------------------------------------
      @Block.slot("1bit", {Image}, required=3)
      def slot_1bit(self, slot, data):
          self.signal_image(data.convert('1'));
          self.reset(slot);

      #-------------------------------------------------------------------------
      @Block.slot("L", {Image}, required=4)
      def slot_L(self, slot, data):
          self.signal_image(data.convert('L'));
          self.reset(slot);

      #-------------------------------------------------------------------------
      @Block.slot("LA", {Image}, required=5)
      def slot_L(self, slot, data):
          self.signal_image(data.convert('LA'));
          self.reset(slot);

      #-------------------------------------------------------------------------
      @Block.slot("P", {Image}, required=6)
      def slot_P(self, slot, data):
          self.signal_image(data.convert('P'));
          self.reset(slot);

      #-------------------------------------------------------------------------
      @Block.slot("PA", {Image}, required=7)
      def slot_P(self, slot, data):
          self.signal_image(data.convert('PA'));
          self.reset(slot);

      #-------------------------------------------------------------------------
      @Block.slot("RGB", {Image}, required=8)
      def slot_rgb(self, slot, data):
          self.signal_image(data.convert('RGB'));
          self.reset(slot);

      #-------------------------------------------------------------------------
      @Block.slot("RGBA", {Image}, required=9)
      def slot_rgba(self, slot, data):
          self.signal_image(data.convert('RGBA'));
          self.reset(slot);

      #-------------------------------------------------------------------------
      @Block.slot("CMYK", {Image}, required=10)
      def slot_cmyk(self, slot, data):
          self.signal_image(data.convert('CMYK'));
          self.reset(slot);

      #-------------------------------------------------------------------------
      @Block.slot("YCbCr", {Image}, required=11)
      def slot_ycbcr(self, slot, data):
          self.signal_image(data.convert('YCbCr'));
          self.reset(slot);

      #-------------------------------------------------------------------------
      @Block.slot("LAB", {Image}, required=12)
      def slot_lab(self, slot, data):
          self.signal_image(data.convert('LAB'));
          self.reset(slot);

      #-------------------------------------------------------------------------
      @Block.slot("HSV", {Image}, required=13)
      def slot_hsv(self, slot, data):
          self.signal_image(data.convert('HSV'));
          self.reset(slot);

      #-------------------------------------------------------------------------
      @Block.slot("I", {Image}, required=14)
      def slot_I(self, slot, data):
          self.signal_image(data.convert('I'));
          self.reset(slot);

      #-------------------------------------------------------------------------
      @Block.slot("F", {Image}, required=15)
      def slot_F(self, slot, data):
          self.signal_image(data.convert('F'));
          self.reset(slot);

      #-------------------------------------------------------------------------
      @Block.signal("image", Image)
      def signal_image(self, data):
          return data;

      #-------------------------------------------------------------------------
      def run(self, **kwarg):
          raise RuntimeError("No tiene sentido invocar el método 'run' de un objeto de clase 'ConvertImage'.");
