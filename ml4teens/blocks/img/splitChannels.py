import PIL;

from PIL.Image import Image;

from ...core import Block;

class SplitChannels(Block):

      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);

      #-------------------------------------------------------------------------
      @Block.slot("image", {Image})
      def slot_frame(self, slot, data):
          mode=data.mode.upper();
          bands=data.getbands();
          channels= data.split();
          assert len(bands)==len(channels), "Formato de imagen no soportado: bands!=channels";
          
          for (band, channel) in zip(bands,channels):

              if band=='1' and self.signal_1bit()       and mode=='1':
                 self.signal_1bit(channel);

              if band=='A' and self.signal_alpha()      and mode=='LA': # + La
                 self.signal_alpha(channel);
              if band=='L' and self.signal_grey()       and mode=='L':
                 self.signal_grey(channel);

              if band=='A' and self.signal_alpha()      and mode=='PA': # + Pa
                 self.signal_alpha(channel);
              if band=='P' and self.signal_palette()    and mode=='P':
                 self.signal_palette(channel);

              if band=='A' and self.signal_alpha()      and mode in ["RGB","RGBA"]: # + RGBa
                 self.signal_alpha(channel);
              if band=='R' and self.signal_red()        and mode in ["RGB","RGBA"]: # + RGBa
                 self.signal_red(channel);
              if band=='G' and self.signal_green()      and mode in ["RGB","RGBA"]: # + RGBa
                 self.signal_green(channel);
              if band=='B' and self.signal_blue()       and mode in ["RGB","RGBA"]: # + RGBa
                 self.signal_blue(channel);

              if band=='C' and self.signal_cyan()       and mode in ["CMYK"]:
                 self.signal_cyan(channel);
              if band=='M' and self.signal_magenta()    and mode in ["CMYK"]:
                 self.signal_magenta(channel);
              if band=='Y' and self.signal_yellow()     and mode in ["CMYK"]:
                 self.signal_yellow(channel);
              if band=='K' and self.signal_black()      and mode in ["CMYK"]:
                 self.signal_black(channel);

              if band=='Y' and self.signal_luminance()  and mode in ["YCBCR"]:
                 self.signal_luminance(channel);
              if band=='Cb' and self.signal_bdiff()     and mode in ["YCBCR"]:
                 self.signal_bdiff(channel);
              if band=='Cr' and self.signal_rdiff()     and mode in ["YCBCR"]:
                 self.signal_rdiff(channel);

              if band=='L' and self.signal_LAB_l()      and mode in ["LAB"]:
                 self.signal_LAB_l(channel);
              if band=='A' and self.signal_LAB_a()      and mode in ["LAB"]:
                 self.signal_LAB_a(channel);
              if band=='B' and self.signal_LAB_b()      and mode in ["LAB"]:
                 self.signal_LAB_b(channel);

              if band=='H' and self.signal_hue()        and mode in ["HSV"]:
                 self.signal_hue(channel);
              if band=='S' and self.signal_saturation() and mode in ["HSV"]:
                 self.signal_saturation(channel);
              if band=='V' and self.signal_value()      and mode in ["HSV"]:
                 self.signal_value(channel);

              if band=='I' and self.signal_I()          and mode in ["I"]:
                 self.signal_I(channel);

              if band=='F' and self.signal_F()          and mode in ["F"]:
                 self.signal_F(channel);

      #-------------------------------------------------------------------------
      @Block.signal("1bit", Image)
      def signal_1bit(self, data):
          return data;
      #-------------------------------------------------------------------------
      @Block.signal("grey", Image)
      def signal_grey(self, data):
          return data;
      #-------------------------------------------------------------------------
      @Block.signal("alpha", Image)
      def signal_alpha(self, data):
          return data;
      #-------------------------------------------------------------------------
      @Block.signal("palette", Image)
      def signal_palette(self, data):
          return data;
      #-------------------------------------------------------------------------
      @Block.signal("red", Image)
      def signal_red(self, data):
          return data;
      #-------------------------------------------------------------------------
      @Block.signal("green", Image)
      def signal_green(self, data):
          return data;
      #-------------------------------------------------------------------------
      @Block.signal("blue", Image)
      def signal_blue(self, data):
          return data;
      #-------------------------------------------------------------------------
      @Block.signal("cyan", Image)
      def signal_cyan(self, data):
          return data;
      #-------------------------------------------------------------------------
      @Block.signal("magenta", Image)
      def signal_magenta(self, data):
          return data;
      #-------------------------------------------------------------------------
      @Block.signal("yellow", Image)
      def signal_yellow(self, data):
          return data;
      #-------------------------------------------------------------------------
      @Block.signal("black", Image)
      def signal_black(self, data):
          return data;
      #-------------------------------------------------------------------------
      @Block.signal("luminance", Image)
      def signal_luminance(self, data):
          return data;
      #-------------------------------------------------------------------------
      @Block.signal("bdiff", Image)
      def signal_bdiff(self, data):
          return data;
      #-------------------------------------------------------------------------
      @Block.signal("rdiff", Image)
      def signal_rdiff(self, data):
          return data;
      #-------------------------------------------------------------------------
      @Block.signal("lab l", Image)
      def signal_LAB_l(self, data):
          return data;
      #-------------------------------------------------------------------------
      @Block.signal("lab a", Image)
      def signal_LAB_a(self, data):
          return data;
      #-------------------------------------------------------------------------
      @Block.signal("lab b", Image)
      def signal_LAB_b(self, data):
          return data;
      #-------------------------------------------------------------------------
      @Block.signal("hue", Image)
      def signal_hue(self, data):
          return data;
      #-------------------------------------------------------------------------
      @Block.signal("saturation", Image)
      def signal_saturation(self, data):
          return data;
      #-------------------------------------------------------------------------
      @Block.signal("value", Image)
      def signal_value(self, data):
          return data;
      #-------------------------------------------------------------------------
      @Block.signal("int", Image)
      def signal_I(self, data):
          return data;
      #-------------------------------------------------------------------------
      @Block.signal("float", Image)
      def signal_F(self, data):
          return data;

