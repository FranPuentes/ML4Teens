# -*- coding: utf-8 -*-

import copy;
import pandas as pd;
import PIL;

from PIL.Image import Image;

import numpy as np;
from sklearn.preprocessing import StandardScaler;
import matplotlib.pyplot as plt;
from mpl_toolkits.mplot3d import Axes3D;
from io import BytesIO;

from ...core import Block;

#===============================================================================
class Plot3D(Block):
      """
      Recibe un DataFrame de Pandas y lo representa, posiblemente con reducción de dimensionalidad.
      
      La reducción se hace en 3D interactiva con el objetivo de representarla
      El slot 'labels' puede recibir otro DataFrame, en cuyo caso usa su primera columna para diferenciar los puntos.
      """
      
      parameters=[{ "name":"clean",     "type":"bool",   "default":"True",                   "doc":"lleva a cabo la limpieza de datos" },
                  { "name":"normalize", "type":"bool",   "default":"True",                   "doc":"lleva a cabo la normalización de los datos" },
                  { "name":"method",    "type":"string", "default":"tsne",                   "doc":"algoritmo de reducción de dimensionalidad" },
                  { "name":"threshold", "type":"float",  "default":"0.5",                    "doc":"(en tanto por uno) elimina columnas nulas" },
                  { "name":"figsize",   "type":"tupla",  "default":"(8,6)",                  "doc":"tamaño de la figura" },
                  { "name":"cmap",      "type":"string", "default":"viridis",                "doc":"mapa de color" },
                  { "name":"marker",    "type":"string", "default":"o",                      "doc":"marcador para los puntos" },
                  { "name":"edgecolor", "type":"string", "default":"k",                      "doc":"color del borde" },
                  { "name":"s",         "type":"string", "default":"50",                     "doc":"tamaño de los puntos" },
                  { "name":"alpha",     "type":"float",  "default":"0.7",                    "doc":"nivel de transparencia de los puntos" },
                  { "name":"title",     "type":"string", "default":"Clusterización",         "doc":"Título del gráfico" },
                  { "name":"xlabel",    "type":"string", "default":"Componente principal 1", "doc":"Etiqueta de las x" },
                  { "name":"ylabel",    "type":"string", "default":"Componente principal 2", "doc":"Etiqueta de las y" },
                  { "name":"inplace",   "type":"bool",   "default":"False",                  "doc":"Muestra la imagen, además de mandarla como señal" },
                 ];
      
      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          self._labels=None;
          
      #-------------------------------------------------------------------------
      def load(self, filename):
          df=pd.read_csv(filename);
          self.context.emit(target=self, slot="dataframe", data=df);
          
      #-------------------------------------------------------------------------
      @Block.slot("labels", {pd.DataFrame})
      def slot_labels(self, slot, data):
          self._labels=data;
          
      #-------------------------------------------------------------------------
      @Block.slot("dataframe", {pd.DataFrame})
      def slot_dataframe(self, slot, data):
          if data is not None:
          
             df=data.copy();
             data=None;

             # Limpiar filas
             # eliminar filas con todo a NaN
             df.dropna(axis=0, how="all", inplace=True);
             
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
                  pca = PCA(n_components=3);
                  df = pca.fit_transform(df);
             elif self.params.method.lower()=="t-sne" or self.params.method.lower()=="tsne":
                  from sklearn.manifold import TSNE;
                  tsne = TSNE(n_components=3);
                  df = tsne.fit_transform(df);
             elif self.params.method.lower()=="lda":
                  assert self._labels is not None, "LDA necesita las etiquetas";
                  from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA;                  
                  labels = self._labels.iloc[:, 0];
                  lda = LDA(n_components=3);
                  df = lda.fit_transform(df, labels);
             elif self.params.method.lower()=="isomap":
                  from sklearn.manifold import Isomap;
                  isomap = Isomap(n_components=3, n_neighbors=self.params.neighbors or max(5, int(np.log10(df.shape[0]))));
                  df = isomap.fit_transform(df);
             else:
                  raise RuntimeError(f"Método de reducción de dimensionalidad desconocido: f{self.params.method}");
                  
             xs = df[:, 0];
             ys = df[:, 1];
             zs = df[:, 2];
                  
             if self._labels is None:
                plt.figure(figsize=self.params.figsize or (10, 6));
                ax = Axes3D(fig);
                plot_geeks = ax.scatter(xs, ys, zs, color='green') ;
                ax.set_title("3D plot") 
                ax.set_xlabel('x-axis') 
                ax.set_ylabel('y-axis') 
                ax.set_zlabel('z-axis') 
                plt.show();
                
             else:
                import plotly.graph_objects as go;
                
                # Crear el gráfico
                fig = go.Figure(data=[go.Scatter3d(
                    x=xs,
                    y=ys,
                    z=zs,
                    mode='markers',
                    marker=dict(
                        size=6,
                        color=self._labels, 
                        colorscale='Viridis', 
                        opacity=0.8,
                        showscale=True 
                    )
                )])

                # Actualizar los layout del gráfico
                fig.update_layout(
                    title='Interactive 3D Scatter Plot by Labels',
                    scene=dict(
                        xaxis_title='X Axis',
                        yaxis_title='Y Axis',
                        zaxis_title='Z Axis'
                    ),
                    margin=dict(l=0, r=0, b=0, t=30)  # Ajustar márgenes
                )

                # Mostrar el gráfico
                fig.show();

             """
             if self._labels is None:
                plt.scatter(df[:, 0],
                            df[:, 1],
                            #cmap=self.params.cmap or 'viridis',
                            marker=self.params.marker or 'o', 
                            edgecolor=self.params.edgecolor or 'k',
                            s=self.params.size or self.params.s or 50,
                            alpha=self.params.alpha or 0.7);
             else:
                target_values = self._labels.iloc[:, 0];
                valores_unicos = target_values.unique();
                for i, target_label in enumerate(valores_unicos):
                    plt.scatter(df[target_values == target_label, 0], 
                                df[target_values == target_label, 1],
                                label=target_label,
                                marker=self.params.marker or 'o',
                                edgecolor=self.params.edgecolor or 'k',
                                s=self.params.size or self.params.s or 50,
                                alpha=self.params.alpha or 0.7);                    
                plt.legend(title="Layenda");
                            
             plt.title (self.params.title  or 'Plot');
             plt.xlabel(self.params.xlabel or 'Componente Principal 1');
             plt.ylabel(self.params.ylabel or 'Componente Principal 2');
             
             # TODO mostrar el gráfico!
             """
