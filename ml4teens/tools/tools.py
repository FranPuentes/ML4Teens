from PIL import Image;
import requests;
from io import BytesIO;

def image_from_url(url:str):
    """
    Esta función recibe como parámetro una url:str y si es posible devuelve una imagen:Image.
    
    Si no puede devolver la imagen dispara una excepción.
    """
    try:
        response = requests.get(url);
        img = Image.open(BytesIO(response.content))
        return img;
        
    except Exception as e:
        raise RuntimeError(f"No he podido cargar la siguiente imagen: {url}");

    