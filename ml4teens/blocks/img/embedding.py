# -*- coding: utf-8 -*-

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

from ...tools import ImgEmbeddings;

#===============================================================================
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
      # Constructor
      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          self._embedder=ImgEmbeddings(model_size=self.params.model or "xs", quantize=bool(self.params.quantize) if self.params.quantize is not None else True);

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
          