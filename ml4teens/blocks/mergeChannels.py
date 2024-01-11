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
      @Block.slot("alpha", {Image})
      def slot_alpha(self, slot, data):
          pass;

      #-------------------------------------------------------------------------
      @Block.slot("1bit", {Image})
      def slot_1bit(self, slot, data):
          self.signal_image(data.convert("1"));

      #-------------------------------------------------------------------------
      @Block.slot("grey", {Image})
      def slot_grey(self, slot, data):
          alpha=self.tokens["alpha"].data;
          if alpha: self.signal_image(merge("LA",(data.convert("L"),aplha)));
          else:     self.signal_image(data.convert("L"));

      #-------------------------------------------------------------------------
      @Block.slot("palette", {Image})
      def slot_palette(self, slot, data):
          alpha=self.tokens["alpha"].data;
          if alpha: self.signal_image(merge("PA",(data.convert("P"),aplha)));
          else:     self.signal_image(data.convert("P"));

      #=========================================================================
      # RGB
      def _rgb(self):
          a=self.tokens["alpha"].data;
          r=self.tokens["red"  ].data;
          g=self.tokens["green"].data;
          b=self.tokens["blue" ].data;
          if all([(c is not None) for c in [r,g,b]]):
             if a: imagen= merge("RGBA",(r,g,b,a));
             else: imagen= merge("RGB", (r,g,b  ));
             self.signal_image(imagen);
             del self.tokens["alpha"];
             del self.tokens["red"  ];
             del self.tokens["green"];
             del self.tokens["blue" ];

      #-------------------------------------------------------------------------
      @Block.slot("red", {Image})
      def slot_red(self, slot, data):
          assert len(data.getbands())==1, "RED debería recibir una imagen de un sólo canal";
          self._rgb();
      #-------------------------------------------------------------------------
      @Block.slot("green", {Image})
      def slot_green(self, slot, data):
          assert len(data.getbands())==1, "GREEN debería recibir una imagen de un sólo canal";
          self._rgb();
      #-------------------------------------------------------------------------
      @Block.slot("blue", {Image})
      def slot_blue(self, slot, data):
          assert len(data.getbands())==1, "BLUE debería recibir una imagen de un sólo canal";
          self._rgb();

      #=========================================================================
      # CMYK
      def _cmyk(self):
          c=self.tokens["cyan"   ].data;
          m=self.tokens["magenta"].data;
          y=self.tokens["yellow" ].data;
          k=self.tokens["black"  ].data;
          if all([(c is not None) for c in [c,m,y,k]]):
             self.signal_image(merge("CMYK",(c,m,y,k)));
             del self.tokens["cyan"   ];
             del self.tokens["magenta"];
             del self.tokens["yellow" ];
             del self.tokens["black"  ];

      #-------------------------------------------------------------------------
      @Block.slot("cyan", {Image})
      def slot_cyan(self, slot, data):
          assert len(data.getbands())==1, "CYAN debería recibir una imagen de un sólo canal";
          self._cmyk();
      #-------------------------------------------------------------------------
      @Block.slot("magenta", {Image})
      def slot_magenta(self, slot, data):
          assert len(data.getbands())==1, "MAGENTA debería recibir una imagen de un sólo canal";
          self._cmyk();
      #-------------------------------------------------------------------------
      @Block.slot("yellow", {Image})
      def slot_yellow(self, slot, data):
          assert len(data.getbands())==1, "YELLOW debería recibir una imagen de un sólo canal";
          self._cmyk();
      #-------------------------------------------------------------------------
      @Block.slot("black", {Image})
      def slot_black(self, slot, data):
          assert len(data.getbands())==1, "BLACK debería recibir una imagen de un sólo canal";
          self._cmyk();

      #=========================================================================
      # YCbCr
      def _ycbcr(self):
          y=self.tokens["luminance"].data;
          b=self.tokens["bdiff"    ].data;
          r=self.tokens["rdiff"    ].data;
          if all([(c is not None) for c in [y,b,r]]):
             self.signal_image(merge("YCbCr",(y,b,r)));
             del self.tokens["luminance"];
             del self.tokens["bdiff"    ];
             del self.tokens["rdiff"    ];

      #-------------------------------------------------------------------------
      @Block.slot("luminance", {Image})
      def slot_luminance(self, slot, data):
          assert len(data.getbands())==1, "LUMINANCE debería recibir una imagen de un sólo canal";
          self._ycbcr();
      #-------------------------------------------------------------------------
      @Block.slot("bdiff", {Image})
      def slot_bdiff(self, slot, data):
          assert len(data.getbands())==1, "BDIF debería recibir una imagen de un sólo canal";
          self._ycbcr();
      #-------------------------------------------------------------------------
      @Block.slot("rdiff", {Image})
      def slot_rdiff(self, slot, data):
          assert len(data.getbands())==1, "RDIFF debería recibir una imagen de un sólo canal";
          self._ycbcr();

      #=========================================================================
      # LAB
      def _lab(self):
          l=self.tokens["lab l"].data;
          a=self.tokens["lab a"].data;
          b=self.tokens["lab b"].data;
          if all([(c is not None) for c in [l,a,b]]):
             self.signal_image(merge("LAB",(l,a,b)));
             del self.tokens["lab l"];
             del self.tokens["lab a"];
             del self.tokens["lab b"];

      #-------------------------------------------------------------------------
      @Block.slot("lab l", {Image})
      def slot_LAB_l(self, slot, data):
          assert len(data.getbands())==1, "LAB-L debería recibir una imagen de un sólo canal";
          self._lab();
      #-------------------------------------------------------------------------
      @Block.slot("lab a", {Image})
      def slot_LAB_a(self, slot, data):
          assert len(data.getbands())==1, "LAB-A debería recibir una imagen de un sólo canal";
          self._lab();
      #-------------------------------------------------------------------------
      @Block.slot("lab b", {Image})
      def slot_LAB_b(self, slot, data):
          assert len(data.getbands())==1, "LAB-B debería recibir una imagen de un sólo canal";
          self._lab();

      #=========================================================================
      # HSV
      def _hsv(self):
          h=self.tokens["hue"       ].data;
          s=self.tokens["saturation"].data;
          v=self.tokens["value"     ].data;
          if all([(c is not None) for c in [h,s,v]]):
             self.signal_image(merge("HSV",(h,s,v)));
             del self.tokens["hue"       ];
             del self.tokens["saturation"];
             del self.tokens["value"     ];

      #-------------------------------------------------------------------------
      @Block.slot("hue", {Image})
      def slot_hub(self, slot, data):
          assert len(data.getbands())==1, "HUE debería recibir una imagen de un sólo canal";
          self._hsv();
      #-------------------------------------------------------------------------
      @Block.slot("saturation", {Image})
      def slot_saturation(self, slot, data):
          assert len(data.getbands())==1, "SATURATION debería recibir una imagen de un sólo canal";
          self._hsv();
      #-------------------------------------------------------------------------
      @Block.slot("value", {Image})
      def slot_value(self, slot, data):
          assert len(data.getbands())==1, "VALUE debería recibir una imagen de un sólo canal";
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

