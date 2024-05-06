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
class ConfusionMatrix(Block):
      """
      A partir de una matriz de confusión, analiza sus principales valores y emite una imagen representativa.
      """
      
      parameters=[{ "name":"", "type":"", "default":"", "doc":"" },
                 ];
      
      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          self._classes = None;
          self._matrix  = None;
          
      #-------------------------------------------------------------------------
      def _process(self):
      
          if self._classes is not None and self._matrix is not None:
          
             # TODO mostrar los valores deducidos principales
          
             from sklearn.metrics import confusion_matrix;
             import seaborn as sns;

             plt.figure(figsize=(10, 7));
             sns.heatmap(self._matrix, annot=True, fmt="d", cmap="Blues", xticklabels=self._classes, yticklabels=self._classes);
             plt.title("Matriz de Confusión");
             plt.ylabel("Verdad");
             plt.xlabel("Inferido");

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
          
             self._classes=None;
             self._matrix =None;
      
      #-------------------------------------------------------------------------
      @Block.slot("classes", {np.ndarray}) 
      def slot_classes(self, slot, data):
          if data is not None:
             self._classes=data;
             self._process();
          
      #-------------------------------------------------------------------------
      @Block.slot("matrix", {np.ndarray}) 
      def slot_matrix(self, slot, data):
          if data is not None:
             assert len(data.shape)==2 and data.shape[0]==data.shape[1], "La matriz de confusión debe ser una matriz cuadrada";
             self._matrix=data;
             self._process();

      #-------------------------------------------------------------------------
      @Block.signal("image", Image)
      def signal_image(self, data):
          return data;
