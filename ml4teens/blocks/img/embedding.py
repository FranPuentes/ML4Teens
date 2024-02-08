import os;
import requests;
import numpy as np;
import PIL;

from tempfile import NamedTemporaryFile;

from PIL.Image import Image;

import torch;

from torch import Tensor;

from ...core import Context; 

from ...core import Block;

#===============================================================================
class Embedding(Block):
      """
      Dada una imagen calcula su embedding.
      """
      
      #-------------------------------------------------------------------------
      class Embedder():
      
            #-------------------------------------------------------------------
            def __init__(self):
            
                if Context().gpu:
                   from transformers import AutoImageProcessor, ViTModel;
                   
                   self._processor = AutoImageProcessor.from_pretrained("google/vit-base-patch16-224-in21k");
                   self._model     = ViTModel.from_pretrained("google/vit-base-patch16-224-in21k");
                
                else:
                   """
                   import mediapipe as mp;
                   from mediapipe.tasks import python;
                   from mediapipe.tasks.python import vision;
                   
                   BaseOptions = mp.tasks.BaseOptions;
                   ImageEmbedder = mp.tasks.vision.ImageEmbedder;
                   ImageEmbedderOptions = mp.tasks.vision.ImageEmbedderOptions;
                   VisionRunningMode = mp.tasks.vision.RunningMode;

                   model_name="mobilenet_v3_small.tflite";
                   if "model" in self.params:
                       if self.params["model"].lower() in ["nano",  "xs"]: model_name="mobilenet_v3_small.tflite";
                       if self.params["model"].lower() in ["small", "s" ]: model_name="mobilenet_v3_small.tflite";
                       if self.params["model"].lower() in ["medium","m" ]: model_name="mobilenet_v3_small.tflite";
                       if self.params["model"].lower() in ["large", "l" ]: model_name="mobilenet_v3_large.tflite";
                       if self.params["model"].lower() in ["xlarge","xl"]: model_name="mobilenet_v3_large.tflite";

                   options = ImageEmbedderOptions(base_options=BaseOptions(model_asset_path=os.path.join(Context().mwd, model_name)),
                                                  quantize=self.params.quantize or True,
                                                  running_mode=VisionRunningMode.IMAGE);

                   self._processor = None;
                   self._model = ImageEmbedder.create_from_options(options);
                   """
                   from imgbeddings import imgbeddings;
                   
                   self._processor = None;
                   self._model = imgbeddings();
                
            #-------------------------------------------------------------------
            def embedding(self, imagen):
                
                if Context().gpu:
                   inputs = self._processor(imagen, return_tensors="pt");
                   with torch.no_grad():
                        outputs = self._model(**inputs);
                        return outputs.last_hidden_state[0];
                
                else:
                   """
                   result = self._model.embed(imagen);
                   return result.embeddings[0].embedding;
                   """
                   embedding = self._model.to_embeddings(imagen);
                   return embedding[0];

      #-------------------------------------------------------------------------
      @staticmethod
      def download(source:str):
          if source.startswith("http"):
             with requests.get(source, stream=True) as r:
                  r.raise_for_status();
                  with NamedTemporaryFile(delete=False) as f:
                       for chunk in r.iter_content(chunk_size=65536//8):
                           f.write(chunk);
                       fuente = f.name;
                       istemp = True;
          else:
             fuente = source;
             istemp = False;
          return (fuente, istemp);

      #-------------------------------------------------------------------------
      # Constructor
      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          self._embedder=Embedding.Embedder();

      #-------------------------------------------------------------------------
      # SLOTS
      #-------------------------------------------------------------------------
      @Block.slot("image",{Image,str})
      def slot_image(self, slot, data:(Image|str)):

          if data and self.signal_embedding():

             assert isinstance(data,(Image,str));

             if   isinstance(data,str):
                  try:
                    fuente, istemp = Embedding.download(data);
                    imagen = PIL.Image.open(fuente);
                    self.signal_embedding(self._embedder.embedding(imagen));
                  finally:
                    if istemp: os.remove(fuente);

             elif isinstance(data,Image):
                  self.signal_embedding(self._embedder.embedding(data));

      #-------------------------------------------------------------------------
      # SIGNALS
      #-------------------------------------------------------------------------
      @Block.signal("embedding",Tensor)
      def signal_embedding(self, data):
          return data;
          