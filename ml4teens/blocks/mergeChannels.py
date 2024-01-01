import cv2 as cv;
import numpy as np;

from PIL.Image import Image, fromarray, merge;

import PIL;

from ..core import Block;

class MergeChannels(Block):

      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);

      #-------------------------------------------------------------------------
      @Block.slot("alpha", {Image}, required=False)
      def slot_alpha(self, slot, data):
          pass;

      #-------------------------------------------------------------------------
      @Block.slot("1bit", {Image}, required=2)
      def slot_1bit(self, slot, data):
          self.signal_image(data.convert("1"));

      #-------------------------------------------------------------------------
      @Block.slot("grey", {Image}, required=3)
      def slot_grey(self, slot, data):
          alpha=self._value("alpha");
          if alpha: self.signal_image(merge("LA",(data.convert("L"),aplha)));
          else:     self.signal_image(data.convert("L"));

      #-------------------------------------------------------------------------
      @Block.slot("palette", {Image}, required=4)
      def slot_palette(self, slot, data):
          alpha=self._value("alpha");
          if alpha: self.signal_image(merge("PA",(data.convert("P"),aplha)));
          else:     self.signal_image(data.convert("P"));

      #=========================================================================
      # RGB
      def _rgb(self):
          a=self._value("alpha");
          r=self._value("red"  );
          g=self._value("green");
          b=self._value("blue" );
          if all([(c is not None) for c in [r,g,b]]):
             if a: imagen= merge("RGBA",(r,g,b,a));
             else: imagen= merge("RGB", (r,g,b  ));
             self.signal_image(imagen);
             self.reset("alpha", "red", "green", "blue");

      #-------------------------------------------------------------------------
      @Block.slot("red", {Image}, required=5)
      def slot_red(self, slot, data):
          assert len(data.getbands())==1, "RED debería recibir una imagen de un sólo canal";
          self._rgb();
      #-------------------------------------------------------------------------
      @Block.slot("green", {Image}, required=5)
      def slot_green(self, slot, data):
          assert len(data.getbands())==1, "GREEN debería recibir una imagen de un sólo canal";
          self._rgb();
      #-------------------------------------------------------------------------
      @Block.slot("blue", {Image}, required=5)
      def slot_blue(self, slot, data):
          assert len(data.getbands())==1, "BLUE debería recibir una imagen de un sólo canal";
          self._rgb();

      #=========================================================================
      # CMYK
      def _cmyk(self):
          c=self._value("cyan"   );
          m=self._value("magenta");
          y=self._value("yellow" );
          k=self._value("black"  );
          if all([(c is not None) for c in [c,m,y,k]]):
             self.signal_image(merge("CMYK",(c,m,y,k)));
             self.reset("cyan", "magenta", "yellow", "black");

      #-------------------------------------------------------------------------
      @Block.slot("cyan", {Image}, required=6)
      def slot_cyan(self, slot, data):
          assert len(data.getbands())==1, "CYAN debería recibir una imagen de un sólo canal";
          self._cmyk();
      #-------------------------------------------------------------------------
      @Block.slot("magenta", {Image}, required=6)
      def slot_magenta(self, slot, data):
          assert len(data.getbands())==1, "MAGENTA debería recibir una imagen de un sólo canal";
          self._cmyk();
      #-------------------------------------------------------------------------
      @Block.slot("yellow", {Image}, required=6)
      def slot_yellow(self, slot, data):
          assert len(data.getbands())==1, "YELLOW debería recibir una imagen de un sólo canal";
          self._cmyk();
      #-------------------------------------------------------------------------
      @Block.slot("black", {Image}, required=6)
      def slot_black(self, slot, data):
          assert len(data.getbands())==1, "BLACK debería recibir una imagen de un sólo canal";
          self._cmyk();

      #=========================================================================
      # YCbCr
      def _ycbcr(self):
          y=self._value("luminance");
          b=self._value("bdiff");
          r=self._value("rdiff");
          if all([(c is not None) for c in [y,b,r]]):
             self.signal_image(merge("YCbCr",(y,b,r)));
             self.reset("luminance", "bdiff", "rdiff");

      #-------------------------------------------------------------------------
      @Block.slot("luminance", {Image}, required=7)
      def slot_luminance(self, slot, data):
          assert len(data.getbands())==1, "LUMINANCE debería recibir una imagen de un sólo canal";
          self._ycbcr();
      #-------------------------------------------------------------------------
      @Block.slot("bdiff", {Image}, required=7)
      def slot_bdiff(self, slot, data):
          assert len(data.getbands())==1, "BDIF debería recibir una imagen de un sólo canal";
          self._ycbcr();
      #-------------------------------------------------------------------------
      @Block.slot("rdiff", {Image}, required=7)
      def slot_rdiff(self, slot, data):
          assert len(data.getbands())==1, "RDIFF debería recibir una imagen de un sólo canal";
          self._ycbcr();

      #=========================================================================
      # LAB
      def _lab(self):
          l=self._value("lab l");
          a=self._value("lab a");
          b=self._value("lab b");
          if all([(c is not None) for c in [l,a,b]]):
             self.signal_image(merge("LAB",(l,a,b)));
             self.reset("lab l", "lab a", "lab b");

      #-------------------------------------------------------------------------
      @Block.slot("lab l", {Image}, required=8)
      def slot_LAB_l(self, slot, data):
          assert len(data.getbands())==1, "LAB-L debería recibir una imagen de un sólo canal";
          self._lab();
      #-------------------------------------------------------------------------
      @Block.slot("lab a", {Image}, required=8)
      def slot_LAB_a(self, slot, data):
          assert len(data.getbands())==1, "LAB-A debería recibir una imagen de un sólo canal";
          self._lab();
      #-------------------------------------------------------------------------
      @Block.slot("lab b", {Image}, required=8)
      def slot_LAB_b(self, slot, data):
          assert len(data.getbands())==1, "LAB-B debería recibir una imagen de un sólo canal";
          self._lab();

      #=========================================================================
      # HSV
      def _hsv(self):
          h=self._value("hue");
          s=self._value("saturation");
          v=self._value("value");
          if all([(c is not None) for c in [h,s,v]]):
             self.signal_image(merge("HSV",(h,s,v)));
             self.reset("hue", "saturation", "value");

      #-------------------------------------------------------------------------
      @Block.slot("hue", {Image}, required=9)
      def slot_hub(self, slot, data):
          assert len(data.getbands())==1, "HUE debería recibir una imagen de un sólo canal";
          self._hsv();
      #-------------------------------------------------------------------------
      @Block.slot("saturation", {Image}, required=9)
      def slot_saturation(self, slot, data):
          assert len(data.getbands())==1, "SATURATION debería recibir una imagen de un sólo canal";
          self._hsv();
      #-------------------------------------------------------------------------
      @Block.slot("value", {Image}, required=9)
      def slot_value(self, slot, data):
          assert len(data.getbands())==1, "VALUE debería recibir una imagen de un sólo canal";
          self._hsv();

      #-------------------------------------------------------------------------
      @Block.slot("int", {Image}, required=10)
      def slot_I(self, slot, data):
          self.signal_image(data.convert('I'));

      #-------------------------------------------------------------------------
      @Block.slot("float", {Image}, required=10)
      def slot_F(self, slot, data):
          self.signal_image(data.convert('F'));

      #-------------------------------------------------------------------------
      @Block.signal("image", Image)
      def signal_image(self, data):
          return data;

      #-------------------------------------------------------------------------
      def run(self, **kwarg):
          raise RuntimeError("No tiene sentido invocar el método 'run' de un objeto de clase 'SplitChannels'.");
          