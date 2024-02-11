from PIL import Image;
import requests;
from io import BytesIO;

# TODO parámetros opciones, modo y tamaño
def image_from_url(url:str, mode=None, width=None, height=None):
    """
    Esta función recibe como parámetro una url:str y si es posible devuelve una imagen:Image.
    
    Si no puede devolver la imagen dispara una excepción.
    """
    try:
      headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'};

      response = requests.get(url, headers=headers);      
      if response.status_code == 200:
         img = Image.open(BytesIO(response.content));
         print(f"Formato: {img.format}, Tamaño: {img.size}, Modo: {img.mode}");
      else:
         raise RuntimeError(f"Error al descargar la imagen: Estado HTTP {response.status_code}");
        
    except Exception as e:
        raise RuntimeError(f"No he podido cargar la siguiente imagen: {url}");

    