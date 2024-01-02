from PIL.Image import Image;

from ..core import Block;

class ResizeImage(Block):

      #-------------------------------------------------------------------------
      # width
      # height
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          if "width" in kwargs:  self._width=kwargs["width"];
          else:                  self._width=None;
          if "height" in kwargs: self._height=kwargs["height"];
          else:                  self._height=None;
          assert self._width  is None or type(self._width)  in [int, float], f"El parámetro 'width' debe ser un tamaño (int) o un factor (float)";
          assert self._height is None or type(self._height) in [int, float], f"El parámetro 'height' debe ser un tamaño (int) o un factor (float)";

      #-------------------------------------------------------------------------
      @Block.slot("shape", {tuple,list, Image}, required=False)
      def slot_shape(self, slot, data):
      
          if   type(data) is tuple and len(data)>=2:
               self._values[slot]=data[:2];
               self.signal_shape(tuple(data[:2]));
               
          elif type(data) is list and len(data)>=2:
               self._values[slot]=data[:2];
               self.signal_shape(tuple(data[:2]));
               
          elif isinstance(data,Image):
               self._values[slot]=(data.width,data.height);
               self.signal_shape((data.width,data.height));
               
          else:
               raise ValueError(f"Tipo no contemplado: {type(data)}");

      #-------------------------------------------------------------------------
      @Block.slot("image", {Image}, required=2)
      def slot_image(self, slot, data):

          assert isinstance(data, Image);

          if "shape" in self._values:
             width =self._values["shape"][0] if self._values["shape"] else self._width ;
             height=self._values["shape"][1] if self._values["shape"] else self._height;
          else:
             width =self._width ;
             height=self._height;

          if width  is not None and type(width ) is float: width =int(data.width *width );
          if height is not None and type(height) is float: height=int(data.height*height);

          if (width is None or width==0) and (height is None or height==0):
             self.signal_image(data);
          else:
             if not width:
                r=height/float(data.height);
                width=int(data.width*r);
                
             if not height:
                r=width/float(data.width);
                height=int(data.height*r);
                
             self.signal_image(data.resize( (width,height) ));
             
          self.reset("image");

      #-------------------------------------------------------------------------
      @Block.signal("image", Image)
      def signal_image(self, data):
          return data;

      #-------------------------------------------------------------------------
      @Block.signal("shape", tuple)
      def signal_shape(self, data):
          return data;

      #-------------------------------------------------------------------------
      def run(self, **kwarg):
          raise RuntimeError("No tiene sentido invocar el método 'run' de un objeto de clase 'ResizeImage'.");
          