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
          
      #-------------------------------------------------------------------------
      @Block.slot("matrix", {np.ndarray, pd.DataFrame}) 
      def slot_matrix(self, slot, data):
          if data is not None:
             assert len(data.shape)==2 and data.shape[0]==data.shape[1], "La matriz de confusión debe ser una matriz cuadrada";
             _classes = data.columns.values;
             _matrix  = data.to_numpy();
             
             # Inicializar las métricas
             precision = []
             recall = []
             specificity = []
             f1_scores = []
             accuracy = None;
             
             # Calcular métricas para cada clase
             for i in range(len(_matrix)):
                 # Verdaderos positivos
                 tp = _matrix[i, i]
                 # Falsos positivos
                 fp = _matrix[:, i].sum() - tp
                 # Falsos negativos
                 fn = _matrix[i, :].sum() - tp
                 # Verdaderos negativos
                 tn = _matrix.sum() - (tp + fp + fn)
                 
                 # Precisión por clase
                 prec = tp / (tp + fp) if (tp + fp) != 0 else 0
                 precision.append(prec)
                 
                 # Recall (sensibilidad) por clase
                 rec = tp / (tp + fn) if (tp + fn) != 0 else 0
                 recall.append(rec)
                 
                 # Especificidad por clase
                 spec = tn / (tn + fp) if (tn + fp) != 0 else 0
                 specificity.append(spec)
                 
                 # F1-score por clase
                 f1 = 2 * (prec * rec) / (prec + rec) if (prec + rec) != 0 else 0
                 f1_scores.append(f1)
             
             # Exactitud global
             accuracy = _matrix.diagonal().sum() / _matrix.sum()
             
             self.signal_metrics( { "classes":_classes, "precision": precision, "recall": recall, "specificity": specificity, "F1": f1_scores, "accuracy": accuracy } );
          
             from sklearn.metrics import confusion_matrix;
             import seaborn as sns;

             plt.figure(figsize=(10, 7));
             sns.heatmap(data, annot=True, fmt="d", cmap="Blues");
             plt.title("Matriz de confusión");
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

      #-------------------------------------------------------------------------
      @Block.signal("image", Image)
      def signal_image(self, data):
          return data;

      #-------------------------------------------------------------------------
      @Block.signal("metrics", dict)
      def signal_metrics(self, data):
          return data;
