# -*- coding: utf-8 -*-

import ipywidgets as widgets;

from IPython.display import display;
from ipywidgets      import Layout, Button, HBox;

from ...core import Block;

#===============================================================================
class DataLabelizer(Block):
      """
      Permite etiquetar datos.      
      """
      
      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          
          self._labels=self.params.labels if self.params.labels is not None else ["Sí","No"];
          self._data  =None;
          
          buttons=[];
          for n,label in enumerate(self._labels):
              button = Button(description=str(label), layout=Layout(width='auto') );
              button.style.button_color = 'Orange';      # Cambiar el color de fondo del botón
              button.layout.width = '200px';             # Cambiar el ancho del botón
              button.layout.height = '30px';             # Cambiar la altura del botón
              button.on_click(lambda _, label=label: self.click_label(label));
              buttons.append(button);
          
          hbox=HBox(buttons, layout=Layout(border='solid'));
          display(hbox);
          
      #-------------------------------------------------------------------------
      def click_label(self, label):
          self.signal_label(  str(label)              );
          self.signal_data ( (str(label), self._data) );
          
      #-------------------------------------------------------------------------
      @Block.slot("data", {object})
      def slot_data(self, slot, data):
          self._data=data;
          
      #-------------------------------------------------------------------------
      @Block.signal("data", tuple)
      def signal_data(self, data):
          return data;
          
      #-------------------------------------------------------------------------
      @Block.signal("label", str)
      def signal_label(self, data):
          return data;
