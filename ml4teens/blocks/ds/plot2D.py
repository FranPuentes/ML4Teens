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
class Plot2D(Block):
      """
      Recibe un DataFrame de Pandas y lo representa, posiblemente con reducción de dimensionalidad.
      
      SLOTS
      + dataframe: Pandas DataFrame.
      
      SIGNALS
      + image: imagen 2D.
      
      PARÁMETROS
      + clean: hacer una limpieza de los datos (booleano, por defecto True)
      + normalize: hacer una normalización de los datos (booleano, por defecto True)
      + method: nombre del algoritmo de reducción de dimensionalidad, por defecto "pca"
      + threshold: (en tanto por uno) elimina columnas si tiene n% elementos a NaN, por defecto 0.5 (50%)
      + figsize: por defecto (8, 6)
      + cmap: por defecto 'viridis'
      + marker: por defecto 'o'
      + edgecolor: por defecto 'k'
      + s | size: por defecto 50
      + alpha: por defecto 0.7
      + title: por defecto "Plot"
      + xlabel: por defecto "Componente Principal 1"
      + ylabel: por defecto "Componente Principal 2"
      + inplace: muestra la imagen, además de mandarla como señal.
      """
      
      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          self._labels=None;
          
      #-------------------------------------------------------------------------
      @Block.slot("labels", {pd.DataFrame})
      def slot_labels(self, slot, data):
          self._labels=data;
          
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
                  
             plt.figure(figsize=self.params.figsize or (8, 6));
             if self._labels is None:
                plt.scatter(df[:, 0],
                            df[:, 1],
                            cmap=self.params.cmap or 'viridis',
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
             
             buf = BytesIO();
             try:
               plt.savefig(buf, format='png');
               buf.seek(0);
               imagen=PIL.Image.open(buf);
               imagen.load();
               self.signal_image(imagen);
               if self.params.inplace: plt.show();
             finally:  
               buf.close();
               plt.close();
             
             return True;
             
          return False;

      #-------------------------------------------------------------------------
      @Block.signal("image", Image)
      def signal_image(self, data):
          return data;

