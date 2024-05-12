# -*- coding: utf-8 -*-

import os;
import zipfile;
import tempfile;
import textwrap;
import random;
import shutil;
import yaml;
import json;

from itertools import accumulate;

from ultralytics import YOLO;

#TODO https://docs.ultralytics.com/es/usage/callbacks/#returning-additional-information-with-prediction

from ...tools import searchFilename, searchPattern;

from ...core import Block;

class YoloTrain(Block):
      """
      Este bloque recibe en el slot 'dataset' el path de un directorio y lleva a cabo el entrenamiento del modelo YOLOv8 indicado en los parámetros.
      Al finalizar el entrenamiento envía la señal 'files' con un diccionario que indica donde están los ficheros resultado.
      
      Este bloque es muy expresivo, va a generar gran cantidad de información técnica.
      Dependiendo del tamaño del dataset y del tamaño del modelo a entrenar, es muy probable que sea necesaria una GPU.
      """
      
      parameters=[{"name":"model",     "type":"string",      "default":"yolov8n.pt", "doc":"Modelo yolo preentrenado a usar."},
                  {"name":"epochs",    "type":"int",         "default":"10",         "doc":"Número de epochs a emplear en el entrenamiento."},
                  {"name":"imgsz",     "type":"int",         "default":"640",        "doc":"Tamaño de la imagen al entrar en el modelo."},
                  {"name":"batch",     "type":"int",         "default":"-1",         "doc":"Tamaño del lote (-1 significa que lo elija el modelo)."},
                  {"name":"patience",  "type":"int",         "default":"100",        "doc":"Condición para un early stop."},
                  {"name":"device",    "type":"string|none", "default":"none",       "doc":"¿Qué dispositvo usar? cuda, cpu."},
                  {"name":"optimizer", "type":"string",      "default":"auto",       "doc":"¿Qué optimizador usar?"},
                  {"name":"seed",      "type":"int",         "default":"0",          "doc":"Semilla, para que el entrenamieto sea reproducible"},
                 ];

      #--------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          self._from_url=None;
          
      #--------------------------------------------------------------------------
      def param(self, key, default=None):
          if key in self.params: return self.params[key];
          else:                  return default;

      #--------------------------------------------------------------------------
      def _train(self, dataset):
          
          os.environ["YOLO_VERBOSE"]="false";
          model = YOLO(task="detect", model=self.param("model","yolov8n.pt"), verbose=False);
          try:
            epochs   =self.param("epochs",       10);
            imgsz    =self.param("imgsz",       640);
            batch    =self.param("batch",        -1);
            patience =self.param("patience",    100);
            device   =self.param("device",     None);
            optimizer=self.param("optimizer","auto");
            seed     =self.param("seed",          0);
            model.train(verbose=False, 
                        imgsz=imgsz, 
                        batch=batch, 
                        epochs=epochs, 
                        data=dataset, 
                        patience=patience,
                        device=device,
                        optimizer=optimizer,
                        seed=seed,
                        project=os.path.abspath("./runs"),
                        name=".", 
                        exist_ok=True, 
                        plots=True);
            
            return os.path.abspath("./runs");
                        
          finally:
            del model;  

      #--------------------------------------------------------------------------
      @Block.slot("dataset", {str})
      def slot_dataset(self, slot, source):
      
          if source:
             
             assert os.path.exists(source), f"El dataset '{source}' no existe!";

             source=os.path.abspath(source);

             results = self._train(source);
             
             if results:
             
                files={ "model":            searchFilename(results, "best.pt"),
                        "args":             searchFilename(results, "args.yaml"),
                        "confusion matrix": searchFilename(results, "confusion_matrix.png"),
                        "F1 curve":         searchFilename(results, "F1_curve.png"),
                        "P curve":          searchFilename(results, "P_curve.png"),
                        "R curve":          searchFilename(results, "R_curve.png"),
                        "PR curve":         searchFilename(results, "PR_curve.png"),
                        "results":          searchFilename(results, "results.csv"),
                        "batchs":           { "train":searchPattern(results,"train_batch*.jpg"), "val":searchPattern(results,"val_batch*.jpg") },
                      };

                self.signal_files(files);
                
             return True;
             
      #--------------------------------------------------------------------------
      @Block.signal("files", dict)
      def signal_files(self, data):
          return data;

      #--------------------------------------------------------------------------
      @Block.slot("close", {object})
      def slot_close(self, slot, data):
          pass;
