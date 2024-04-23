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
      Lleva a cabo un clustering dado un DataFrame de Pandas.
      Esta clase NO detecta el número de clusters 'óptimo', debe indicarse.
      
      SLOTS
      + dataframe: Pandas DataFrame.
      
      SIGNALS
      + image: imagen 2D del clustering.
      
      PARÁMETROS
      + clean: hacer una limpieza de los datos (booleano, por defecto True)
      + normalize: hacer una normalización de los datos (booleano, por defecto True)
      + clusters: el número de clusters buscados, por defecto 2
      + method: nombre del algoritmo de reducción de dimensionalidad, por defecto "tsne"
      + algorithm: nombre del algoritmo de clustering, por defecto "kmeans"
      + args: diccionario de parámetros para el algoritmo de clusterización
      + threshold: (en tanto por uno) elimina columnas si tiene n% elementos a NaN, por defecto 0.5 (50%)
      + figsize: por defecto (8, 6)
      + cmap: por defecto 'viridis'
      + marker: por defecto 'o'
      + edgecolor: por defecto 'k'
      + s | size: por defecto 50
      + alpha: por defecto 0.7
      + title: por defecto "Clusterización"
      + xlabel: por defecto "Componente Principal 1"
      + ylabel: por defecto "Componente Principal 2"
      """
      
      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          self._target=None;
          
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
          return data;
