# -*- coding: utf-8 -*-
import os;
import PIL;
import numpy as np;

from PIL.Image import Image;

import torch;

#===============================================================================
class ImgEmbeddings():

      #-------------------------------------------------------------------
      def __init__(self, model_size=None, quantize=True):

          from ..core import Context;
          
          if Context().gpu:
             import transformers;
             
             transformers.utils.logging.disable_progress_bar();
             transformers.utils.logging.set_verbosity=transformers.logging.ERROR;
             
             from transformers import AutoImageProcessor, ViTModel;

             self._processor = AutoImageProcessor.from_pretrained("google/vit-base-patch16-224-in21k");
             self._model     = ViTModel.from_pretrained("google/vit-base-patch16-224-in21k");

          else:
             import mediapipe as mp;
             from mediapipe.tasks import python;
             from mediapipe.tasks.python import vision;
               
             BaseOptions = mp.tasks.BaseOptions;
             ImageEmbedder = mp.tasks.vision.ImageEmbedder;
             ImageEmbedderOptions = mp.tasks.vision.ImageEmbedderOptions;
             VisionRunningMode = mp.tasks.vision.RunningMode;

             _model_name="mobilenet_v3_small.tflite";
             if model_size:
                if model_size.lower() in ["nano",  "xs"]: _model_name="mobilenet_v3_small.tflite";
                if model_size.lower() in ["small", "s" ]: _model_name="mobilenet_v3_small.tflite";
                if model_size.lower() in ["medium","m" ]: _model_name="mobilenet_v3_small.tflite";
                if model_size.lower() in ["large", "l" ]: _model_name="mobilenet_v3_large.tflite";
                if model_size.lower() in ["xlarge","xl"]: _model_name="mobilenet_v3_large.tflite";

             options = ImageEmbedderOptions(base_options=BaseOptions(model_asset_path=os.path.join(Context().mwd, _model_name)),
                                            quantize=quantize,
                                            running_mode=VisionRunningMode.IMAGE);
                          
             self._processor = None;
             self._model = ImageEmbedder.create_from_options(options);

      #-------------------------------------------------------------------
      def embedding(self, imagen):
          
          from ..core import Context;
          
          if Context().gpu:
             inputs = self._processor(imagen, return_tensors="pt");
             with torch.no_grad():
                  outputs = self._model(**inputs);
                  embedding=outputs.last_hidden_state[0];
                  return embedding;

          else:
             import mediapipe as mp;
             
             match imagen.mode:
             
                   case "L":    image = mp.Image(image_format=mp.ImageFormat.GRAY8, data=np.asarray(imagen));
                   case "RGB":  image = mp.Image(image_format=mp.ImageFormat.SRGBA, data=np.asarray(imagen));
                   case "HSV":  image = mp.Image(image_format=mp.ImageFormat.SRGBA, data=np.asarray(imagen));
                   case "LAB":  image = mp.Image(image_format=mp.ImageFormat.SRGBA, data=np.asarray(imagen));
                   case "RGBA": image = mp.Image(image_format=mp.ImageFormat.SRGB,  data=np.asarray(imagen));
                   case _:      raise f"Formato de imagen no soportada: {imagen.mode}";
             
             result = self._model.embed(image);
             embedding = result.embeddings[0].embedding;          
             return torch.from_numpy(embedding);

#===============================================================================
class TxtEmbeddings():

      #-------------------------------------------------------------------
      def __init__(self, quantize=True):

          from ..core import Context;
          
          import mediapipe as mp;
          from mediapipe.tasks import python;
          from mediapipe.tasks.python import text;
            
          BaseOptions = mp.tasks.BaseOptions;
          TextEmbedder = mp.tasks.text.TextEmbedder;
          TextEmbedderOptions = mp.tasks.text.TextEmbedderOptions;

          model_name="universal_sentence_encoder.tflite";

          options = TextEmbedderOptions(base_options=BaseOptions(model_asset_path=os.path.join(Context().mwd, model_name)), quantize=quantize);
                       
          self._processor = None;
          self._model = TextEmbedder.create_from_options(options);

      #-------------------------------------------------------------------
      def embedding(self, texto):
          
          result = self._model.embed(texto);
          embedding = result.embeddings[0].embedding;          
          return torch.from_numpy(embedding);

