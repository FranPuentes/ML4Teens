from PIL.Image import Image;

from ...core import Block;

class ResizeImage(Block):

      #-------------------------------------------------------------------------
      # width : None | int | float
      # height: None | int | float
      def __init__(self, **kwargs):
          super().__init__(**kwargs);

          self._width =self.params.width;
          self._height=self.params.height;

          assert isinstance(self._width,  (int, float, type(None))), f"El parámetro 'width' debe ser un tamaño (int) o un factor (float)";
          assert isinstance(self._height, (int, float, type(None))), f"El parámetro 'height' debe ser un tamaño (int) o un factor (float)";

      #-------------------------------------------------------------------------
      @Block.slot("shape", {tuple,list,Image})
      def slot_shape(self, slot, data):
      
          if   type(data) is tuple and len(data)>=2:
               self._width, self._height = data[:2];
               self.signal_shape(tuple(data[:2]));
               
          elif type(data) is list and len(data)>=2:
               self._width, self._height = data[:2];
               self.signal_shape(tuple(data[:2]));
               
          elif isinstance(data,Image):
               self._width, self._height = data.width, data.height;
               self.signal_shape((data.width,data.height));
               
          else:
               raise ValueError(f"Tipo no contemplado: {type(data)}");

      #-------------------------------------------------------------------------
      @Block.slot("image", {Image})
      def slot_image(self, slot, data):

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
             
      #-------------------------------------------------------------------------
      @Block.signal("image", Image)
      def signal_image(self, data):
          return data;

      #-------------------------------------------------------------------------
      @Block.signal("shape", tuple)
      def signal_shape(self, data):
          return data;

