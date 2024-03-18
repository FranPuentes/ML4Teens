
import pandas as pd;

from ..core import Block;

#===============================================================================
class YoloDataSource(Block):

      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          
      #-------------------------------------------------------------------------
      @Block.slot("source",{str})
      def slot_source(self, slot, data):
          """
          Recibe la url o el nombre de un fichero .zip; si es una url la descarga.
          Descomprime el contenido en ./<name>
          Comprueba el directorio ./<name>/data
          Crea el directorio ./<name>/tmp
          Crea el directorio ./<name>/run
          Crea el fichero ./<name>/tmp/dataset.yaml a partir de ./<name>/dataset.yaml
          Envía la señal signal_dataset con './<name>' como parámetro.
          """
          pass;
          
      #-------------------------------------------------------------------------
      @Block.signal("dataset", str)
      def signal_dataset(self, data):
          return data;
          