import sys, os;
import PIL;
import requests;

from tempfile import NamedTemporaryFile;
from PIL.Image import Image;

from ...core import Block;

class ImageSource(Block):

      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          self.width =self.params.width;
          self.height=self.params.height;

      #-------------------------------------------------------------------------
      @Block.signal("image", Image)
      def signal_image(self, data):
          return data;

      #-------------------------------------------------------------------------
      @Block.signal("histogram", list)
      def signal_histogram(self, data):
          return data;

      #-------------------------------------------------------------------------
      @Block.signal("dims", tuple)
      def signal_dims(self, data):
          return data;

      #-------------------------------------------------------------------------
      @Block.signal("info", dict)
      def signal_info(self, data):
          return data;

      #-------------------------------------------------------------------------
      def _resize(self, imagen, width, height):
      
          if width is None and height is None:
             return imagen;
             
          else:
             if width==imagen.width and height==imagen.height:
                return imagen;
                
             if not width:
                r=height/float(imagen.height);
                width=int(imagen.width*r);

             if not height:
                r=width/float(imagen.width);
                height=int(imagen.height*r);

             return imagen.resize( (width,height) );
      
      
      
      
      @Block.slot("source", {str})
      def slot_source(self, slot, fuente):
      
          #TODO normalizar las imágenes, no podemos manejar tantos 'mode'
          
          #TODO considerar que fuente pueda ser un directorio => procesar todas las imágenes en él
          #     en este caso, que se pueda indicar un patrón (*.jpg, por ejemplo).

          def shapeof(imagen):
              ancho, alto = imagen.size;
              modo = imagen.mode;
              if   modo == 'RGB':   canales = 3;
              elif modo == 'LAB':   canales = 3;
              elif modo == 'HSV':   canales = 3;
              elif modo == 'RGBA':  canales = 4;
              elif modo == 'CMYK':  canales = 4;
              elif modo == 'YCbCr': canales = 4;
              elif modo == 'L':     canales = 1;
              elif modo == 'P':     canales = 1;
              elif modo == '1':     canales = 1;
              elif modo == 'I':     canales = 1;
              elif modo == 'F':     canales = 1;
              else:                 canales = None;
              return (ancho, alto, canales);

          def histogramas(imagen):
              modo = imagen.mode;
              histograma_completo = imagen.histogram();
              if   modo == '1'    or modo == 'L' or modo == 'P' or modo == 'I' or modo == 'F': return [histograma_completo];
              elif modo == 'RGB'  or modo == 'YCbCr':                                          return [histograma_completo[i:i+256] for i in range(0, 768,  256)];
              elif modo == 'RGBA' or modo == 'CMYK':                                           return [histograma_completo[i:i+256] for i in range(0, 1024, 256)];
              elif modo == 'LAB'  or modo == 'HSV':                                            return [histograma_completo[i:i+256] for i in range(0, 768,  256)];
              else:                                                                            return None;

          istemp=False;
          if fuente.startswith("http"):
             with requests.get(fuente, stream=True) as r:
                  r.raise_for_status();
                  with NamedTemporaryFile(delete=False, suffix='.img') as f:
                       for chunk in r.iter_content(chunk_size=65536//8):
                           f.write(chunk);
                       fuente = f.name;
                       istemp=True;

          try:
            with PIL.Image.open(fuente) as imagen:
            
                 if self.signal_info():
                    info={"format":imagen.format, "size":imagen.size, "mode":imagen.mode, "palette":imagen.palette, "exif":imagen._getexif(), "info":imagen.info };
                    self.signal_info(info);

                 if self.signal_dims():
                    shape=shapeof(imagen);
                    self.signal_dims(shape);

                 if self.signal_histogram():
                    self.signal_histogram(histogramas(imagen));
 
                 if self.signal_image():
                    imagen.load();
                    self.signal_image(self._resize(imagen, self.width, self.height));

          finally:
            if istemp:
               os.remove(fuente);
