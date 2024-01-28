import IPython;

from IPython.display import update_display, display;

from PIL.Image import Image;

from ..core import Block;

class Display(Block):

      #-------------------------------------------------------------------------
      # width
      # height
      # feed = False
      def __init__(self, *args, **kwargs):
          super().__init__(*args, **kwargs);
          self._handle=None;
          
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
          if data:
             width =self.params.width;
             height=self.params.height;
             imagen=self._redim(data,width,height);
             #TODO motrar 'title', si hay ...
             if not self.params.feed:
                if self._handle is None:
                   self._handle=display(imagen, display_id=self._id);
                else:
                   self._handle.update(imagen);
             else:                    
                display(imagen);
          self.signal_image(data);

