import IPython;

from IPython.display import update_display;

from PIL.Image import Image;

from ..core import Block;

class Display(Block):

      #-------------------------------------------------------------------------
      # width
      # height
      # feed = False
      def __init__(self, *args, **kwargs):
          super().__init__(*args, **kwargs);
          self._feed=bool(self.params.get("feed",False));

      #-------------------------------------------------------------------------
      @Block.signal("image", Image)
      def signal_image(self, data):
          return data;

      #-------------------------------------------------------------------------
      def _redim(self, imagen, width=None, height=None):

          if width is None and height is None: return imagen;
          
          (w, h) = imagen.width, imagen.height;
          
          if width is None:
             r = height / float(h);
             dimensiones = (int(w * r), height);
          else:
             r = width / float(w);
             dimensiones = (width, int(h * r));
             
          imagen = imagen.resize(dimensiones);
                
          return imagen;

      #-------------------------------------------------------------------------
      @Block.slot("image", {Image})
      def slot_image(self, slot, data):
          width =self.params.width;
          height=self.params.height;
          imagen=self._redim(data,width,height);
          if self._feed==False: update_display(imagen, display_id=self._id);
          else:                 display(imagen);
          self.signal_image(data);

