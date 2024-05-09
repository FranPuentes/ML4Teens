# -*- coding: utf-8 -*-

import copy;
import pandas as pd;
import PIL;

from PIL.Image import Image;

from sklearn.base import BaseEstimator;

import numpy as np;
from sklearn.preprocessing import StandardScaler;
import matplotlib.pyplot as plt;
from io import BytesIO;

from ...core import Block;

#===============================================================================
class Clustering(Block):
      """
      Lleva a cabo un agrupamiento (clustering) 2D dado un DataFrame de Pandas y, opcionalmente, una columna objetivo (target).
      En 'target' recibe un Dataframe, cuya primera columna será usada para la validación del 'clustering'.
      REn 'dataframe' recibe uno, aplica el agrupamiento y genera la señal "image".
      
      Opcionalmente los datos de entrada se normalizarán y limpiarán antes de su procesamiento.
      Seguidamente se llevará a cabo un método de reducción de dimensionaldad, siempre a 2 componentes.
      Finalmente se realiza el agrupamiento y se genera el gráfico.
      Esta clase no detecta el número de clusters 'óptimo', se debe indicar.
      """
      
      #TODO emitir un dataframe con las agrupaciones realizadas.
      
      parameters=[{ "name":"clean",     "type":"bool",   "default":"True",                   "doc":"lleva a cabo la limpieza de datos" },
                  { "name":"normalize", "type":"bool",   "default":"True",                   "doc":"lleva a cabo la normalización de los datos" },
                  { "name":"clusters",  "type":"int",    "default":"2",                      "doc":"número de clusters a considerar" },
                  { "name":"method",    "type":"bool",   "default":"True",                   "doc":"Usar un algoritmo de reducción de dimensionalidad" },
                  { "name":"algorithm", "type":"string", "default":"kmeans",                 "doc":"algoritmo de clustering a usar (por ahora sólo k-means)" },
                  { "name":"args",      "type":"dict",   "default":"{}",                     "doc":"parámetros para el algoritmo de clustering" },
                  { "name":"threshold", "type":"float",  "default":"0.5",                    "doc":"(en tanto por uno) elimina columnas si tienen dicho porcentaje de elementos a NaN" },
                  { "name":"figsize",   "type":"tupla",  "default":"(8,6)",                  "doc":"tamaño de la figura" },
                  { "name":"cmap",      "type":"string", "default":"viridis",                "doc":"mapa de color" },
                  { "name":"marker",    "type":"string", "default":"o",                      "doc":"marcador para los puntos" },
                  { "name":"edgecolor", "type":"string", "default":"k",                      "doc":"color del borde" },
                  { "name":"s",         "type":"string", "default":"50",                     "doc":"tamaño de los puntos" },
                  { "name":"alpha",     "type":"float",  "default":"0.7",                    "doc":"nivel de transparencia de los puntos" },
                  { "name":"title",     "type":"string", "default":"Clusterización",         "doc":"Título del gráfico" },
                  { "name":"xlabel",    "type":"string", "default":"Componente principal 1", "doc":"Etiqueta de las x" },
                  { "name":"ylabel",    "type":"string", "default":"Componente principal 2", "doc":"Etiqueta de las y" },
                  
                  { "name":"model",     "type":"object", "default":"None",                   "doc":"Modelo preentrenado para hacer inferencia" },
                 ];
      
      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          self._model =self.params.model if isinstance(self.params.model, BaseEstimator) else None;
          self._target=None;
          
      #-------------------------------------------------------------------------
      def load(self, filename):
          df=pd.read_csv(filename);
          self.context.emit(target=self, slot="dataframe", data=df);

      #-------------------------------------------------------------------------
      @Block.slot("model", {BaseEstimator})
      def slot_model(self, slot, data):
          if data is not None:
             self._model=data;
          
      #-------------------------------------------------------------------------
      def _cleanDataframe(self, df):
          # Limpiar filas
          # Eliminar filas con todo a NaN
          df.dropna(axis=0, how="all", inplace=True);
             
          # Limpiar columnas
          # TODO columnas categóricas
          # Elimina columnas con todo a NaN
          df.dropna(axis=1, how="all", inplace=True);
          # Elimina columnas con más del umbral % a NaN
          umbral = len(df) * (self.params.threshold or 0.5);
          df.dropna(axis=1, thresh=int(umbral), inplace=True);
          # Rellena NaN con la media
          df.fillna(df.mean(), inplace=True);
          
          return df;
                  
      #-------------------------------------------------------------------------
      @Block.slot("inference", {pd.DataFrame, list, tuple})
      def slot_inference(self, slot, data):
          if data is not None:
             if self._model is not None:
                _map=self._model._map;
                if isinstance(data, pd.DataFrame):
                   data = data.to_numpy();
                   if self._model._dimr is not None:
                      data=self._model._dimr.transform(data);
                   result = self._model.predict(data);
                   self.signal_prediction( (result, _map) );
                   return;
                if isinstance(data, list):
                   data = pd.DataFrame(data);
                   data = data.to_numpy();
                   if self._model._dimr is not None:
                      data=self._model._dimr.transform(data);
                   result = self._model.predict(data);
                   self.signal_prediction( (result, _map) );
                   return;
                if isinstance(data, tuple):
                   assert len(data)==2 and isinstance(data[1],list)
                   label=data[0];
                   data =data[1];
                   if all([isinstance(t, dict) for t in data]): # lista de diccionarios con claves [index, score, name]
                      print(data);
                      data   ={t["name"]:[t["score"]] for t in data};
                      data = pd.DataFrame(data);
                      data = data.to_numpy();
                      if self._model._scaler is not None:
                         data=self._model._scaler.transform(data);
                      if self._model._dimr is not None:
                         data=self._model._dimr.transform(data);
                      result = self._model.predict(data);
                      self.signal_prediction( (result[0], _map) );
                      return;
                   if all([isinstance(t, list) for t in data]): # lista de listas
                      lista=data;
                      for data in lista:
                          if all([isinstance(t, dict) for t in data]): # lista de diccionarios con claves [index, score, name]
                             data   ={t["name"]:[t["score"]] for t in data};
                             data = pd.DataFrame(data);
                             data = data.to_numpy();
                             if self._model._scaler is not None:
                                data=self._model._scaler.transform(data);
                             if self._model._dimr is not None:
                                data=self._model._dimr.transform(data);
                             result = self._model.predict(data);
                             self.signal_prediction( (result[0], _map) );
                             return;
          
      #-------------------------------------------------------------------------
      @Block.signal("prediction", tuple)
      def signal_prediction(self, data):
          return data;
      
      #-------------------------------------------------------------------------
      @Block.slot("target", {pd.DataFrame}) 
      def slot_target(self, slot, data):
          self._target=data;
          
      #-------------------------------------------------------------------------
      @Block.slot("dataframe", {pd.DataFrame})
      def slot_dataframe(self, slot, data):
          if data is not None:
             df=data.copy();

             if self.params.clean or True:
                df=self._cleanDataframe(df);

             scaler=None;
             # Normalizar el dataframe
             if self.params.normalize or True:
                scaler = StandardScaler();
                df = scaler.fit_transform(df.to_numpy());
                
             dimr=None;   
             if self.params.method is None or bool(self.params.method) is True:
                if df.shape[1]>2:
                   # Reducir la dimensionalidad
                   if self._target is None:
                      from sklearn.decomposition import PCA;
                      dimr = PCA(n_components=self.params.components or 0.99);
                      df = dimr.fit_transform(df);
                   else:
                      from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA;
                      labels = self._target.iloc[:, 0];
                      max_components = self.params.components or min(labels.nunique() - 1, df.shape[1]);
                      dimr = LDA(n_components=max_components);
                      df = dimr.fit_transform(df, labels);
                   
             args     = self.params.args or {};
             clusters = (self._target.iloc[:,0].nunique() if self._target is not None else (self.params.clusters or 2));
             cmodel   = None;
             
             # Realizar clustering
             if   self.params.algorithm is None or self.params.algorithm.lower()=="kmeans": # por defecto
                  from sklearn.cluster import KMeans;
                  cmodel = KMeans(n_clusters=clusters, **args);
                  clusters = cmodel.fit_predict(df);
                  labels = pd.DataFrame(clusters, columns=['__TARGET__']);
                  self.signal_labels(labels);
                  cmodel._scaler = scaler;
                  cmodel._dimr   = dimr;
                  if self._target is not None:
                     _map={}; 
                     for i, l in enumerate(self._target.iloc[:,0]):
                         _map[l]=clusters[i];
                     cmodel._map=_map;
                  else:
                     cmodel._map=None;                     
             elif self.params.algorithm.lower()=="agglomerative":
                  from sklearn.cluster import AgglomerativeClustering;
                  cmodel = AgglomerativeClustering(n_clusters=clusters, **args);
                  clusters =cmodel.fit_predict(df);
                  labels = pd.DataFrame(clusters, columns=['__TARGET__']);
                  self.signal_labels(labels);
                  cmodel._scaler = scaler;
                  cmodel._dimr   = dimr;
                  if self._target is not None:
                     _map={}; 
                     for i, l in enumerate(self._target.iloc[:,0]):
                         _map[l]=clusters[i];
                     cmodel._map=_map;
                  else:
                     cmodel._map=None;                     
             elif self.params.algorithm.lower()=="dbscan":
                  from sklearn.cluster import DBSCAN;
                  cmodel = DBSCAN(**args);
                  clusters = cmodel.fit_predict(df);
                  labels = pd.DataFrame(clusters, columns=['__TARGET__']);
                  self.signal_labels(labels);
                  cmodel._scaler = scaler;
                  cmodel._dimr   = dimr;
                  if self._target is not None:
                     _map={}; 
                     for i, l in enumerate(self._target.iloc[:,0]):
                         _map[l]=clusters[i];
                     cmodel._map=_map;
                  else:
                     cmodel._map=None;                     
             elif self.params.algorithm.lower()=="spectral":
                  from sklearn.cluster import SpectralClustering;
                  cmodel = SpectralClustering(n_clusters=clusters, **args);
                  clusters = cmodel.fit_predict(df);
                  clusters =cmodel.fit_predict(df);
                  labels = pd.DataFrame(clusters, columns=['__TARGET__']);
                  self.signal_labels(labels);
                  cmodel._scaler = scaler;
                  cmodel._dimr   = dimr;
                  if self._target is not None:
                     _map={}; 
                     for i, l in enumerate(self._target.iloc[:,0]):
                         _map[l]=clusters[i];
                     cmodel._map=_map;
                  else:
                     cmodel._map=None;                     
             elif self.params.algorithm.lower()=="gaussian" or self.params.algorithm.lower()=="gss":
                  from sklearn.mixture import GaussianMixture;
                  cmodel = GaussianMixture(n_components=clusters, **args);
                  cmodel.fit(df);
                  clusters = cmodel.predict(df);
                  labels = pd.DataFrame(clusters, columns=['__TARGET__']);
                  self.signal_labels(labels);
                  cmodel._scaler = scaler;
                  cmodel._dimr   = dimr;
                  if self._target is not None:
                     _map={}; 
                     for i, l in enumerate(self._target.iloc[:,0]):
                         _map[l]=clusters[i];
                     cmodel._map=_map;
                  else:
                     cmodel._map=None;                     
             else:
                  raise RuntimeError(f"Algoritmo de clusterig desconocido: f{self.params.algorithm}");
             
             self.signal_model(cmodel);
             
             if self._target is not None:
                target_labels = self._target.iloc[:, 0];
                target_index  = target_labels.map(cmodel._map);
                
                from sklearn.metrics import confusion_matrix;

                mat_confusion = confusion_matrix(target_index, clusters);
                
                df_confusion = pd.DataFrame(mat_confusion, index=cmodel._map.keys(), columns=cmodel._map.keys())
                
                self.signal_matrix(df_confusion);
             
      #-------------------------------------------------------------------------
      @Block.signal("labels", pd.DataFrame)
      def signal_labels(self, data):
          return data;
          
      #-------------------------------------------------------------------------
      @Block.signal("matrix", pd.DataFrame)
      def signal_matrix(self, data):
          return data;
          
      #-------------------------------------------------------------------------
      @Block.signal("model", BaseEstimator)
      def signal_model(self, data):
          return data;
