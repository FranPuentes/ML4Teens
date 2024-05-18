# -*- coding: utf-8 -*-
import os;
import PIL;
import numpy as np;

#from PIL.Image import Image;

import torch;

from keras.applications.vgg16 import VGG16;

#===============================================================================
class ImgEmbeddings():

      #-------------------------------------------------------------------
      def __init__(self, model_size=None, quantize=True):
          """
          from ..core import Context;
          
          if Context().gpu:
             import transformers;
             
             transformers.utils.logging.disable_progress_bar();
             transformers.utils.logging.set_verbosity=transformers.logging.ERROR;
             
             from transformers import AutoImageProcessor, ViTModel;
             
             checkpoint="nateraw/vit-base-beans";
             #checkpoint="google/vit-base-patch16-224-in21k";
 
             self._processor = AutoImageProcessor.from_pretrained(checkpoint);
             self._model     = ViTModel.from_pretrained(checkpoint);

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
          """
          self._model = VGG16(weights='imagenet', include_top=False, pooling='max', input_shape=(224, 224, 3));

          for layer in self._model.layers:
              layer.trainable = False;

      #-------------------------------------------------------------------
      def embedding(self, imagen):
          """
          
          if Context().gpu:
             inputs = self._processor(imagen, return_tensors="pt");
             with torch.no_grad():
                  outputs   = self._model(**inputs);
                  embedding = outputs.last_hidden_state[0];
                  embedding = torch.flatten(embedding);
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
          """
          def resize_image(imagen, size=(224, 224)):
              if isinstance(imagen, np.ndarray):
                 imagen = Image.fromarray(imagen);
              imagen = imagen.resize(size, PIL.Image.LANCZOS);
              imagen_array = np.array(imagen);
              return imagen_array;
              
          image = resize_image(imagen);
          image_array = np.expand_dims(image, axis = 0);
          image_embedding = self._model.predict(image_array);
          return torch.from_numpy(image_embedding);

         
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

