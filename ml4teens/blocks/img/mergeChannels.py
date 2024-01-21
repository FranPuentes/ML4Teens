import cv2 as cv;
import numpy as np;

from PIL.Image import Image, fromarray, merge;

import PIL;

from ...core import Block;

class MergeChannels(Block):

      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          
          self._alpha      = None;
          self._red        = None;
          self._green      = None;
          self._blue       = None;
          self._cyan       = None;
          self._magenta    = None;
          self._yellow     = None;
          self._black      = None;
          self._luminance  = None;
          self._bdiff      = None;
          self._rdiff      = None;
          self._lab_l      = None;
          self._lab_a      = None;
          self._lab_b      = None;
          self._hue        = None;
          self._saturation = None;
          self._value      = None;
          

      #-------------------------------------------------------------------------
      @Block.slot("alpha", {Image})
      def slot_alpha(self, slot, data):
          self._alpha=data; 

      #-------------------------------------------------------------------------
      @Block.slot("1bit", {Image})
      def slot_1bit(self, slot, data):
          self.signal_image(data.convert("1"));

      #-------------------------------------------------------------------------
      @Block.slot("grey", {Image})
      def slot_grey(self, slot, data):
          alpha=self._alpha;
          if alpha: self.signal_image(merge("LA",(data.convert("L"),alpha)));
          else:     self.signal_image(data.convert("L"));
          self._alpha=None;

      #-------------------------------------------------------------------------
      @Block.slot("palette", {Image})
      def slot_palette(self, slot, data):
          alpha=self._alpha;
          if alpha: self.signal_image(merge("PA",(data.convert("P"),aplha)));
          else:     self.signal_image(data.convert("P"));
          self._alpha=None;

      #=========================================================================
      # RGB
      def _rgb(self):
          a=self._alpha;
          r=self._red;
          g=self._green;
          b=self._blue;
          if all([(c is not None) for c in [r,g,b]]):
             if a: imagen= merge("RGBA",(r,g,b,a));
             else: imagen= merge("RGB", (r,g,b  ));
             self.signal_image(imagen);
             self._alpha=None;
             self._red  =None;
             self._green=None;
             self._blue =None;

      #-------------------------------------------------------------------------
      @Block.slot("red", {Image})
      def slot_red(self, slot, data):
          if data is None: return;
          assert len(data.getbands())==1, "RED debería recibir una imagen de un sólo canal";
          self._red=data;
          self._rgb();
          
      #-------------------------------------------------------------------------
      @Block.slot("green", {Image})
      def slot_green(self, slot, data):
          if data is None: return;
          assert len(data.getbands())==1, "GREEN debería recibir una imagen de un sólo canal";
          self._green=data;
          self._rgb();
          
      #-------------------------------------------------------------------------
      @Block.slot("blue", {Image})
      def slot_blue(self, slot, data):
          if data is None: return;
          assert len(data.getbands())==1, "BLUE debería recibir una imagen de un sólo canal";
          self._blue=data;
          self._rgb();

      #=========================================================================
      # CMYK
      def _cmyk(self):
          c=self._cyan;
          m=self._magenta;
          y=self._yellow;
          k=self._black;
          if all([(c is not None) for c in [c,m,y,k]]):
             self.signal_image(merge("CMYK",(c,m,y,k)));
             self._cyan   =None;
             self._magenta=None;
             self._yellow =None;
             self._black  =None;

      #-------------------------------------------------------------------------
      @Block.slot("cyan", {Image})
      def slot_cyan(self, slot, data):
          if data is None: return;
          assert len(data.getbands())==1, "CYAN debería recibir una imagen de un sólo canal";
          self._cyan=data;
          self._cmyk();
          
      #-------------------------------------------------------------------------
      @Block.slot("magenta", {Image})
      def slot_magenta(self, slot, data):
          if data is None: return;
          assert len(data.getbands())==1, "MAGENTA debería recibir una imagen de un sólo canal";
          self._magenta=data;
          self._cmyk();
          
      #-------------------------------------------------------------------------
      @Block.slot("yellow", {Image})
      def slot_yellow(self, slot, data):
          if data is None: return;
          assert len(data.getbands())==1, "YELLOW debería recibir una imagen de un sólo canal";
          self._yellow=data;
          self._cmyk();
          
      #-------------------------------------------------------------------------
      @Block.slot("black", {Image})
      def slot_black(self, slot, data):
          if data is None: return;
          assert len(data.getbands())==1, "BLACK debería recibir una imagen de un sólo canal";
          self._black=data;
          self._cmyk();

      #=========================================================================
      # YCbCr
      def _ycbcr(self):
          y=self._luminance;
          b=self._bdiff;
          r=self._rdiff;
          if all([(c is not None) for c in [y,b,r]]):
             self.signal_image(merge("YCbCr",(y,b,r)));
             self._luminance=None;
             self._bdiff    =None;
             self._rdiff    =None;

      #-------------------------------------------------------------------------
      @Block.slot("luminance", {Image})
      def slot_luminance(self, slot, data):
          if data is None: return;
          assert len(data.getbands())==1, "LUMINANCE debería recibir una imagen de un sólo canal";
          self._luminance=data;
          self._ycbcr();
          
      #-------------------------------------------------------------------------
      @Block.slot("bdiff", {Image})
      def slot_bdiff(self, slot, data):
          if data is None: return;
          assert len(data.getbands())==1, "BDIF debería recibir una imagen de un sólo canal";
          self._bdiff=data;
          self._ycbcr();
          
      #-------------------------------------------------------------------------
      @Block.slot("rdiff", {Image})
      def slot_rdiff(self, slot, data):
          if data is None: return;
          assert len(data.getbands())==1, "RDIFF debería recibir una imagen de un sólo canal";
          self._rdiff=data;
          self._ycbcr();

      #=========================================================================
      # LAB
      def _lab(self):
          l=self._lab_l;
          a=self._lab_a;
          b=self._lab_b;
          if all([(c is not None) for c in [l,a,b]]):
             self.signal_image(merge("LAB",(l,a,b)));
             self._lab_l=None;
             self._lab_a=None;
             self._lab_b=None;

      #-------------------------------------------------------------------------
      @Block.slot("lab l", {Image})
      def slot_LAB_l(self, slot, data):
          if data is None: return;
          assert len(data.getbands())==1, "LAB-L debería recibir una imagen de un sólo canal";
          self._lab_l=data;
          self._lab();
          
      #-------------------------------------------------------------------------
      @Block.slot("lab a", {Image})
      def slot_LAB_a(self, slot, data):
          if data is None: return;
          assert len(data.getbands())==1, "LAB-A debería recibir una imagen de un sólo canal";
          self._lab_a=data;
          self._lab();
          
      #-------------------------------------------------------------------------
      @Block.slot("lab b", {Image})
      def slot_LAB_b(self, slot, data):
          if data is None: return;
          assert len(data.getbands())==1, "LAB-B debería recibir una imagen de un sólo canal";
          self._lab_b=data;
          self._lab();

      #=========================================================================
      # HSV
      def _hsv(self):
          h=self._hue;
          s=self._saturation;
          v=self._value;
          if all([(c is not None) for c in [h,s,v]]):
             self.signal_image(merge("HSV",(h,s,v)));
             self._hue=None;
             self._saturation=None;
             self._value=None;

      #-------------------------------------------------------------------------
      @Block.slot("hue", {Image})
      def slot_hub(self, slot, data):
          if data is None: return;
          assert len(data.getbands())==1, "HUE debería recibir una imagen de un sólo canal";
          self._hue=data;
          self._hsv();
          
      #-------------------------------------------------------------------------
      @Block.slot("saturation", {Image})
      def slot_saturation(self, slot, data):
          if data is None: return;
          assert len(data.getbands())==1, "SATURATION debería recibir una imagen de un sólo canal";
          self._saturation=data;
          self._hsv();
          
      #-------------------------------------------------------------------------
      @Block.slot("value", {Image})
      def slot_value(self, slot, data):
          if data is None: return;
          assert len(data.getbands())==1, "VALUE debería recibir una imagen de un sólo canal";
          self._value=data;
          self._hsv();

      #-------------------------------------------------------------------------
      @Block.slot("int", {Image})
      def slot_I(self, slot, data):
          self.signal_image(data.convert('I'));

      #-------------------------------------------------------------------------
      @Block.slot("float", {Image})
      def slot_F(self, slot, data):
          self.signal_image(data.convert('F'));

      #-------------------------------------------------------------------------
      @Block.signal("image", Image)
      def signal_image(self, data):
          return data;

