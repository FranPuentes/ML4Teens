from PIL import Image;
import requests;
from io import BytesIO;

#===============================================================================
def image_from_url(url:str, mode:str=None, width:int=None, height:int=None):
    """
    Esta función recibe como parámetro una url:str y si es posible devuelve una imagen:Image.
    
    Si se indica el mode:str, se convertirá la imagen a dicho formato.
    
    Si se indica width:int o height:int, se redimensionará la imagen.
    
    Si no puede devolver la imagen dispara una excepción.
    """
    try:
      headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'};

      response = requests.get(url, headers=headers);      
      if response.status_code == 200:
         img = Image.open(BytesIO(response.content));
         
         img.load();
         
         if width is not None or height is not None:
         
            original_width, original_height = img.size
         
            if width is not None and height is None:
               ratio = width / original_width;
               new_height = int(original_height * ratio);
               new_dimensions = (width, new_height);
           
            elif height is not None and width is None:
               ratio = height / original_height
               new_width = int(original_width * ratio)
               new_dimensions = (new_width, height)
           
            else:
               new_dimensions = (original_width, original_height)
               
            img = img.resize(new_dimensions, Image.ANTIALIAS);
         
         if mode is not None: return img.convert(mode);
         else:                return img;
         
      else:
         raise RuntimeError(f"Error al descargar la imagen: Estado HTTP {response.status_code}");
        
    except Exception as e:
        raise RuntimeError(f"No he podido cargar la siguiente imagen: {url}");

    