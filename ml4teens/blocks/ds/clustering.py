# -*- coding: utf-8 -*-

import copy;
import pandas as pd;
import PIL;

from PIL.Image import Image;

import numpy as np;
from sklearn.preprocessing import StandardScaler;
import matplotlib.pyplot as plt;
from io import BytesIO;

from ...core import Block;

#===============================================================================
class Clustering(Block):
      """
      Lleva a cabo un agrupamiento (clustering) 2D dado un DataFrame de Pandas y, opcionalmente, una columna objetivo (target).
      
      Opcionalmente los datos de entrada se normalizarán y limpiarán antes de su procesamiento.
      Seguidamente se llevará a cabo un método de reducción de dimensionaldad, siempre a 2 componentes.
      Finalmente se realiza el agrupamiento y se genera el gráfico.
      Esta clase no detecta el número de clusters 'óptimo', se debe indicar.
      """
      
      #TODO emitir un dataframe con las agrupaciones realizadas.
      
      parameters=[{ "name":"clean",     "type":"bool",   "default":"True",                   "doc":"lleva a cabo la limpieza de datos" },
                  { "name":"normalize", "type":"bool",   "default":"True",                   "doc":"lleva a cabo la normalización de los datos" },
                  { "name":"clusters",  "type":"int",    "default":"2",                      "doc":"número de clusters a considerar" },
                  { "name":"method",    "type":"string", "default":"tsne",                   "doc":"algoritmo de reducción de dimensionalidad a usar" },
                  { "name":"algorithm", "type":"string", "default":"kmeans",                 "doc":"algoritmo de clustering a usar" },
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
          self._target=None;
          
      #-------------------------------------------------------------------------
      @Block.slot("target", {pd.DataFrame}) 
      def slot_target(self, slot, data):
          """
          Recibe un Dataframe de Pandas, cuya primera columna será usada para la validación del 'clustering'.
          """
          self._target=data;
          
      #-------------------------------------------------------------------------
      @Block.slot("dataframe", {pd.DataFrame})
      def slot_dataframe(self, slot, data):
          """
          Recibe un Dataframe Pandas, aplica el agrupamiento y genera la señal "image".
          """
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

             # Reducir la dimensionalidad
             if   self.params.method is None or self.params.method.lower()=="pca":
                  from sklearn.decomposition import PCA;
                  pca = PCA(n_components=2);
                  df = pca.fit_transform(df);
             elif self.params.method.lower()=="t-sne" or self.params.method.lower()=="tsne":
                  from sklearn.manifold import TSNE;
                  tsne = TSNE(n_components=2);
                  df = tsne.fit_transform(df);
             elif self.params.method.lower()=="lda":
                  from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA;
                  lda = LDA(n_components=2);
                  df = lda.fit_transform(df, labels);
             elif self.params.method.lower()=="isomap":
                  from sklearn.manifold import Isomap;
                  isomap = Isomap(n_components=2);
                  df = isomap.fit_transform(df);
             else:
                  raise RuntimeError(f"Método de reducción de dimensionalidad desconocido: f{self.params.method}");
                  
             args = (self.params.args if self.params.args is not None else {});

             # Realizar clustering
             if   self.params.algorithm is None or self.params.algorithm.lower()=="kmeans":
                  from sklearn.cluster import KMeans;
                  kmeans = KMeans(n_clusters=self.params.clusters or 2, **args);
                  clusters = kmeans.fit_predict(df);
             elif self.params.algorithm.lower()=="dbscan":
                  from sklearn.cluster import DBSCAN
                  dbscan = DBSCAN(**args);
                  #db = dbscan.fit(df);
                  #labels = db.labels_
                  # Number of clusters in labels, ignoring noise if present.
                  #n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
                  #n_noise_ = list(labels).count(-1)
                  #print("Estimated number of clusters: %d" % n_clusters_)
                  #print("Estimated number of noise points: %d" % n_noise_)
                  clusters = dbscan.fit_predict(df);
             elif self.params.algorithm.lower()=="agglomerative":
                  from sklearn.cluster import AgglomerativeClustering;
                  agglomerative = AgglomerativeClustering(n_clusters=self.params.clusters or 2, **args);
                  clusters = agglomerative.fit_predict(df);
             elif self.params.algorithm.lower()=="spectral":
                  from sklearn.cluster import SpectralClustering;
                  spectral = SpectralClustering(n_clusters=self.params.clusters or 2, **args);
                  clusters = spectral.fit_predict(df);             
             elif self.params.algorithm.lower()=="gaussian" or self.params.algorithm.lower()=="gmm":
                  from sklearn.mixture import GaussianMixture;
                  gmm = GaussianMixture(**args);
                  gmm.fit(df);
                  clusters = gmm.predict(df);
             else:
                  raise RuntimeError(f"Algoritmo de clusterig desconocido: f{self.params.algorithm}");

             # Mostrar la clusterización en una gráfica y enviarla
             plt.figure(figsize=self.params.figsize or (8, 6));
             
             if self._target is None:
                plt.scatter(df[:, 0],
                            df[:, 1],
                            c=clusters,
                            cmap=self.params.cmap or 'viridis',
                            marker=self.params.marker or 'o', 
                            edgecolor=self.params.edgecolor or 'k',
                            s=self.params.size or self.params.s or 50,
                            alpha=self.params.alpha or 0.7);
             else:             
                target_values = self._target.iloc[:, 0];
                
                from sklearn.preprocessing import LabelEncoder

                encoder = LabelEncoder()
                target_values_encoded = encoder.fit_transform(target_values)

                target_values_array = target_values_encoded

                from sklearn.metrics import confusion_matrix
                import seaborn as sns

                # Suponiendo que target_values_array y clusters están correctamente alineados
                # y que ambos son arrays de Numpy del mismo tamaño.

                # Calcula la matriz de confusión
                mat_confusion = confusion_matrix(target_values_array, clusters)

                # Visualización de la matriz de confusión con Seaborn
                plt.figure(figsize=(10, 7))
                sns.heatmap(mat_confusion, annot=True, fmt="d", cmap="Blues",
                            xticklabels=encoder.classes_, yticklabels=encoder.classes_)  # Ajusta las etiquetas según sea necesario
                plt.title("Matriz de Confusión")
                plt.ylabel("Etiquetas Verdaderas")
                plt.xlabel("Etiquetas de Clustering")

                """
                target_values = self._target.iloc[:, 0];
                valores_unicos = target_values.unique();
                for i, target_label in enumerate(valores_unicos):
                    plt.scatter(df[target_values == target_label, 0], 
                                df[target_values == target_label, 1],
                                label=target_label,
                                #c=clusters,
                                #cmap=self.params.cmap or 'viridis',
                                marker=self.params.marker or 'o',
                                edgecolor=self.params.edgecolor or 'k',
                                s=self.params.size or self.params.s or 50,
                                alpha=self.params.alpha or 0.7);                                                                
                plt.legend(title="Clusters");
                """
                                
             #plt.title (self.params.title  or 'Clusterización');
             #plt.xlabel(self.params.xlabel or 'Componente Principal 1');
             #plt.ylabel(self.params.ylabel or 'Componente Principal 2');
             
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
             
          return False;

      #-------------------------------------------------------------------------
      @Block.signal("image", Image)
      def signal_image(self, data):
          """
          Emite una imagen representando una vista 2D de los clusters detectados en el Dataframe de Pandas recibido.
          """
          return data;

