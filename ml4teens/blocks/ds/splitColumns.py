# -*- coding: utf-8 -*-

import copy;
import pandas as pd;

from ...core import Block;

#===============================================================================
class SplitColumns(Block):
      """
      Dado un dataframe, divide las columnas en dos grupos, según la configuración indicada.
      
      SLOTS
      + dataframe: Pandas dataframe.
      
      SIGNALS
      + partition: Pandas dataframe con las columnas indicadas.
      + main: Pandas dataframe con el resto de las columnas.
      
      PARÁMETROS
      + partition | columns: lista de nombres o un nombre, por defecto "__TARGET__".
      
      MÉTODOS
      + load(filename, columns=None): lee un dataframe, hace el split y emite las señales indicadas antes.
      """
      
      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          
      #-------------------------------------------------------------------------
      def split(self, df, columns):
      
          if isinstance(columns,str):
             columns=[columns];
         
          df_included = df[columns].copy(deep=True);
          df_excluded = df.drop(columns=columns, inplace=False);
          
          return df_excluded, df_included;    
          
      #-------------------------------------------------------------------------
      def load(self, filename, columns=None):
          data=pd.read_csv(filename);
          main, partition = self.split(data, columns or self.params.partition or self.params.columns or "__TARGET__");
          self.signal_partition(partition);
          self.signal_main(main);
      
      #-------------------------------------------------------------------------
      @Block.slot("dataframe", {pd.DataFrame})
      def slot_label(self, slot, data):
          if data is not None:
             main, partition = self.split(data, self.params.partition or self.params.columns or "__TARGET__");
             self.signal_partition(partition);
             self.signal_main(main);
             return True;
          return False;

      #-------------------------------------------------------------------------
      @Block.signal("main", pd.DataFrame)
      def signal_main(self, data):
          return data;

      #-------------------------------------------------------------------------
      @Block.signal("partition", pd.DataFrame)
      def signal_partition(self, data):
          return data;
