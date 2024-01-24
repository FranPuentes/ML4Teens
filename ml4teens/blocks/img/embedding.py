import os;
import requests;
import numpy as np;
import PIL;

from tempfile import NamedTemporaryFile;

from PIL.Image import Image;

from transformers import ViTFeatureExtractor, ViTModel;
import torch;

from torch import Tensor;

from ...core import Block;

class Embedding(Block):
      """
      Dada una imagen calcula su embedding.
      """

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
      @staticmethod
      def embedding(fextr, model, imagen):
          inputs  = fextr(images=imagen, return_tensors="pt");
          with torch.no_grad():
               outputs = model(**inputs);
               return outputs.last_hidden_state[0];
               #return torch.mean(outputs.last_hidden_state[0], dim=0).numpy();

      #-------------------------------------------------------------------------
      # Constructor
      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          self._fextr = ViTFeatureExtractor.from_pretrained('google/vit-base-patch16-224')
          self._model = ViTModel.from_pretrained('google/vit-base-patch16-224')

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
                    self.signal_embedding(Embedding.embedding(self._fextr, self._model, imagen));
                  finally:
                    if istemp: os.remove(fuente);

             elif isinstance(data,Image):
                  self.signal_embedding(Embedding.embedding(self._fextr, self._model, data));

      #-------------------------------------------------------------------------
      # SIGNALS
      #-------------------------------------------------------------------------
      @Block.signal("embedding",Tensor)
      def signal_embedding(self, data):
          return data;
          