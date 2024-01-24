import os;
import requests;
import numpy as np;
import PIL;

from PIL.Image import Image;

import torch;
from torch import Tensor;

from ...core import Block;

class Similarity(Block):
      """
      Dados dos embeddings, calcula su similitud.
      """

      #-------------------------------------------------------------------------
      # Constructor
      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          self._1emb  = None;
          self._2emb  = None;

      #-------------------------------------------------------------------------
      def _similarity(self):
          if self._1emb is not None and self._2emb is not None:
             emb1 = self._1emb.numpy().flatten();
             emb2 = self._2emb.numpy().flatten();
             norm1 = emb1 / np.linalg.norm(emb1);
             norm2 = emb2 / np.linalg.norm(emb2);
             similarity = np.dot(norm1, norm2);
             self.signal_similarity(similarity.item());

      #-------------------------------------------------------------------------
      # SLOTS
      #-------------------------------------------------------------------------
      @Block.slot("embedding",{Tensor})
      def slot_embedding(self, slot, data:Tensor):

          if data is None:
             self._1emb=None;
             self._2emb=None;

          else:
             if self._1emb is None:
                self._1emb=data;
                self._2emb=None;

             else:
                self._2emb=data;
                self._similarity();

      #-------------------------------------------------------------------------
      @Block.slot("one",{Tensor})
      def slot_one(self, slot, data:Tensor):
          self._1emb=data;
          self._similarity();

      #-------------------------------------------------------------------------
      @Block.slot("two",{Tensor})
      def slot_two(self, slot, data:Tensor):
          self._2emb=data;
          self._similarity();

      #-------------------------------------------------------------------------
      # SIGNALS
      #-------------------------------------------------------------------------
      @Block.signal("similarity",float)
      def signal_similarity(self, data:float):
          return data;
