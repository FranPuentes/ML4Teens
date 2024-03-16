
import ipywidgets as widgets;
from IPython.display import display;

from ...core import Block;

#===============================================================================
class DataLabelizer(Block):
      """
      Permite etiquetar datos.      
      """
      
      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          
          self._labels=None;
          self._data  =None;          
          
          button = widgets.Button(description="Hola!");
          button.style.button_color = 'lightgreen';  # Cambiar el color de fondo del botón
          button.style.font_weight = 'bold';         # Cambiar el peso de la fuente a negrita
          button.layout.width = '200px';             # Cambiar el ancho del botón
          button.layout.height = '40px';             # Cambiar la altura del botón
          button.layout.border = '2px solid black';  # Agregar un borde al botón
          button.on_click(lambda _: None);
          display(button);
          
      #-------------------------------------------------------------------------
      @Block.slot("data", {object})
      def slot_data(self, slot, data):
          self._data=data;
          
      #-------------------------------------------------------------------------
      @Block.signal("data", object)
      def signal_data(self, data):
          return data;
          
      #-------------------------------------------------------------------------
      @Block.signal("label", str)
      def signal_label(self, data):
          return data;
