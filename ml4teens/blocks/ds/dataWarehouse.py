# -*- coding: utf-8 -*-

import copy;
import pandas as pd;
import numpy  as np;

from ...core import Block;

#===============================================================================
class DataWarehouse(Block):
      """
      Almacén de datos estructurados.
      Básicament un wrap alrededor de un DataFrame de Pandas.
      Permite:
      * leer y escribir en/a un fichero.
      * recibir 'features' en formato "lista de diccionarios con claves 'name' y 'score'", cada lista es una instancia.
      * recibir una etiqueta, que será la etiqueta de los features recibidos mientras no reciba otra.
      
      'name' será de tipo string.
      'score' será numérico. Si es de tipo string se intentará convertir a número, si no es posible se almacena.
      
      Parámetros:
      * self.params.filename: nombre del fichero por defecto.
      * self.params.label_name: nombre de la etiqueta, por defecto es "__TARGET__".
      * self.params.label: valor de la etiqueta por defecto.
      
      TODO:
      * recibir features en otros formatos
      """
      
      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          
          self._df   =None;
          self._label=None;
          
      #-------------------------------------------------------------------------
      @property
      def dataframe(self):
          return self._df;

      #-------------------------------------------------------------------------
      def load(self, filename=None):
          self._df=pd.read_csv(filename if bool(filename) else self.params.filename);
      
      #-------------------------------------------------------------------------
      def save(self, filename=None):
          if self._df is not None:
             self._df.to_csv(filename if bool(filename) else self.params.filename, index=False);
      
      #-------------------------------------------------------------------------
      def append(self, data):
      
          if isinstance(data,tuple) and len(data)==2:
             # tupla de label, data.
             label=data[0];
             self._label=label;
             if self._label is not None and self.params.labelName is None:
                self.params.labelName="__TARGET__";
             data =data[1];
             self.append(data);
             return;
             
          if isinstance(data,list) and all(isinstance(d,list) for d in data):
             # lista de listas.
             for item in data: self.append(item);
             return;
             
          if isinstance(data,list) and all(isinstance(d,dict) and all(key in d for key in ["name","score"]) for d in data):
             # lista de diccionarios con claves 'name' y 'score'.
             inst={};
             for item in data:
                 inst[item["name"]]=item["score"];
             self.append(inst);    
             return;    
             
          if isinstance(data,dict):
             # diccionario, las claves son las columnas.
             inst=copy.copy(data);
             if self.params.labelName:
                inst[self.params.labelName]=self._label if self._label is not None else self.params.label;
             if self._df is None: self._df = pd.DataFrame([inst]);
             else:                self._df = pd.concat( [ self._df, pd.DataFrame([inst]) ], ignore_index=True);
      
          if isinstance(data,np.ndarray):
             # array de numpy
             if   len(data.shape)==1:
                  data=data.reshape(1, -1);
                  if self._df is None: self._df = pd.DataFrame(data);
                  else:                self._df = pd.concat( [ self._df, pd.DataFrame(data) ], ignore_index=True);
             elif len(data.shape)==2:
                  for d in dat.Ta:
                      self.append(d);
             else:
                  raise RuntimeError(f"Array numpy de dimensiones erróneas: {data.shape}");
             
      #-------------------------------------------------------------------------
      @Block.slot("label", {int, float, str})
      def slot_label(self, slot, data):
          self._label=data;
          if self._label is not None and self.params.labelName is None:
             self.params.labelName="__TARGET__";             
          
      #-------------------------------------------------------------------------
      @Block.slot("instance", {tuple,list,dict, np.ndarray})
      def slot_features(self, slot, data):
          if data is not None:
             if self.params.fit is not None: data=self.params.fit(data);
             if data is not None:
                self.append(data);
                self.signal_dataframe(self._df);

      #-------------------------------------------------------------------------
      @Block.signal("dataframe", pd.DataFrame)
      def signal_dataframe(self, data):
          return data;
