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
                  { "name":"method",    "type":"bool",   "default":"False",                  "doc":"Usar un algoritmo de reducción de dimensionalidad" },
                  { "name":"algorithm", "type":"string", "default":"agglomerative",          "doc":"algoritmo de clustering a usar" },
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
                 ];
      
      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          self._model =None;
          self._target=None;
          
      #-------------------------------------------------------------------------
      @Block.slot("model", {BaseEstimator})
      def slot_model(self, slot, data):
          if data is not None:
             self._model=data;
          
      #-------------------------------------------------------------------------
      @Block.slot("inference", {pd.DataFrame})
      def slot_inference(self, slot, data):
          if data is not None:
             if self._model is not None:
                result = self._model.predict(data);
                print(result);
          
      #-------------------------------------------------------------------------
      @Block.slot("target", {pd.DataFrame}) 
      def slot_target(self, slot, data):
          self._target=data;
          
      #-------------------------------------------------------------------------
      @Block.slot("dataframe", {pd.DataFrame})
      def slot_dataframe(self, slot, data):
          if data is not None:
             df=data.copy();

             # Limpiar filas
             # TODO eliminar filas con todo a NaN
             
             # Limpiar columnas
             if self.params.clean or True:
                # TODO columnas categóricas
                # Elimina columnas con todo a NaN
                df.dropna(axis=1, how="all", inplace=True);
                # Elimina columnas con más del umbral % a NaN
                umbral = len(df) * (self.params.threshold or 0.5);
                df.dropna(axis=1, thresh=int(umbral), inplace=True);
                # Rellena NaN con la media
                df.fillna(df.mean(), inplace=True);

             # Normalizar el dataframe
             if self.params.normalize or True:
                scaler = StandardScaler();
                df = scaler.fit_transform(df);
                
             if bool(self.params.method) is True:
                if df.shape[1]>2:
                   # Reducir la dimensionalidad
                   if self._target is None:
                      from sklearn.decomposition import PCA;
                      pca = PCA(n_components=self.params.components or 0.99);
                      df = pca.fit_transform(df);
                   else:
                      from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA;
                      labels = self._target.iloc[:, 0];
                      max_components = min(labels.nunique() - 1, df.shape[1]);
                      lda = LDA(n_components=self.params.components or max_components);
                      df = lda.fit_transform(df, labels);
                   
             args     = self.params.args or {};
             clusters = (self._target.iloc[:,0].nunique() if self._target is not None else (self.params.clusters or 2));
             cmodel   = None;
             
             # Realizar clustering
             if   self.params.algorithm is None or self.params.algorithm.lower()=="agglomerative":
                  from sklearn.cluster import AgglomerativeClustering;
                  cmodel = AgglomerativeClustering(n_clusters=clusters, **args);
                  clusters =cmodel.fit_predict(df);
             elif self.params.algorithm.lower()=="kmeans":
                  from sklearn.cluster import KMeans;
                  cmodel = KMeans(n_clusters=clusters, **args);
                  clusters = cmodel.fit_predict(df);
             elif self.params.algorithm.lower()=="dbscan":
                  assert self._target is None and self._target is None;
                  from sklearn.cluster import DBSCAN;
                  cmodel = DBSCAN(**args);
                  clusters = cmodel.fit_predict(df);
             elif self.params.algorithm.lower()=="spectral":
                  from sklearn.cluster import SpectralClustering;
                  cmodel = SpectralClustering(n_clusters=clusters, **args);
                  clusters = cmodel.fit_predict(df);
             elif self.params.algorithm.lower()=="gaussian" or self.params.algorithm.lower()=="gmm":
                  assert self._target is None and self._target is None;
                  from sklearn.mixture import GaussianMixture;
                  cmodel = GaussianMixture(**args);
                  cmodel.fit(df);
                  clusters = cmodel.predict(df);
             else:
                  raise RuntimeError(f"Algoritmo de clusterig desconocido: f{self.params.algorithm}");

             if self._target is not None:
                target_values = self._target.iloc[:, 0];
                
                from sklearn.preprocessing import LabelEncoder;
                encoder = LabelEncoder();
                target_values_array = encoder.fit_transform(target_values);

                from sklearn.metrics import confusion_matrix;

                mat_confusion = confusion_matrix(target_values_array, clusters);
                
                self.signal_classes(encoder.classes_);
                self.signal_matrix (mat_confusion);
                
                cmodel._encoder=encoder;
             
             self.signal_model(cmodel);
             
             if self._target is None:
                pass;
                
                """
                if df.shape[1]>2:
                   from sklearn.manifold import TSNE;
                   tsne = TSNE(n_components=2);
                   df2  = tsne.fit_transform(df);
                else:
                   df2=df;   

                plt.figure(figsize=self.params.figsize or (8, 6));
                plt.scatter(df2[:, 0],
                            df2[:, 1],
                            c=clusters,
                            cmap=self.params.cmap or 'viridis',
                            marker=self.params.marker or 'o', 
                            edgecolor=self.params.edgecolor or 'k',
                            s=self.params.size or self.params.s or 50,
                            alpha=self.params.alpha or 0.7);
                 """           
             else:
                pass;
                
                """
                target_values = self._target.iloc[:, 0];
                
                from sklearn.preprocessing import LabelEncoder;
                encoder = LabelEncoder();
                target_values_array = encoder.fit_transform(target_values);

                from sklearn.metrics import confusion_matrix;

                # Calcula la matriz de confusión
                mat_confusion = confusion_matrix(target_values_array, clusters);
                
                self.signal_classes(encoder.classes_);
                self.signal_matrix (mat_confusion);
                
                from sklearn.metrics import confusion_matrix;
                import seaborn as sns;

                # Calcula la matriz de confusión
                mat_confusion = confusion_matrix(target_values_array, clusters);

                # Visualización de la matriz de confusión con Seaborn
                plt.figure(figsize=(10, 7));
                sns.heatmap(mat_confusion, 
                            annot=True, 
                            fmt="d", 
                            cmap="Blues",
                            xticklabels=encoder.classes_, 
                            yticklabels=encoder.classes_)  # Ajusta las etiquetas según sea necesario

                plt.title("Matriz de Confusión");
                plt.ylabel("Verdad");
                plt.xlabel("Inferido");
                """
                """
                if df.shape[1]>2:
                   from sklearn.manifold import TSNE;
                   tsne = TSNE(n_components=2);
                   df2  = tsne.fit_transform(df);
                else:
                   df2=df;   
                
                plt.figure(figsize=self.params.figsize or (8, 6));
                target_values = self._target.iloc[:, 0];
                valores_unicos = target_values.unique();
                for i, target_label in enumerate(valores_unicos):
                    plt.scatter(df2[target_values == target_label, 0],
                                df2[target_values == target_label, 1],
                                label=target_label,
                                #c=clusters,
                                #cmap=self.params.cmap or 'viridis',
                                marker=self.params.marker or 'o',
                                edgecolor=self.params.edgecolor or 'k',
                                s=self.params.size or self.params.s or 50,
                                alpha=self.params.alpha or 0.7);
                plt.legend(title="Clusters");
                """
             """                   
             plt.title (self.params.title  or 'Clusterización');
             plt.xlabel(self.params.xlabel or 'Componente 1');
             plt.ylabel(self.params.ylabel or 'Componente 2');
             
             buf = BytesIO();
             try:
               plt.savefig(buf, format='png');
               buf.seek(0);
               imagen=PIL.Image.open(buf);
               imagen.load();
               self.signal_image(imagen);
             finally:  
               buf.close();
               plt.close();
             
             return True;
             """
             
          #return False;

      #-------------------------------------------------------------------------
      @Block.signal("classes", np.ndarray)
      def signal_classes(self, data):
          return data;

      #-------------------------------------------------------------------------
      @Block.signal("matrix", np.ndarray)
      def signal_matrix(self, data):
          return data;
          
      #-------------------------------------------------------------------------
      @Block.signal("model", BaseEstimator)
      def signal_model(self, data):
          return data;
