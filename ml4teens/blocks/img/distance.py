import os;
import requests;
import numpy as np;
import PIL;

from PIL.Image import Image;

import torch;
from torch import Tensor;

from ...core import Block;

class Distance(Block):
      """
      Dados dos embeddings, calcula su distancia.
      """

      #-------------------------------------------------------------------------
      # Constructor
      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          self._1emb = None;
          self._2emb = None;

      #-------------------------------------------------------------------------
      def _distance(self):
          if self._1emb is not None and self._2emb is not None:
             distance = torch.norm(self._1emb - self._2emb);
             self.signal_distance(distance.item());

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
                self._distance();

      #-------------------------------------------------------------------------
      @Block.slot("one",{Tensor})
      def slot_one(self, slot, data:Tensor):
          self._1emb=data;
          self._distance();

      #-------------------------------------------------------------------------
      @Block.slot("two",{Tensor})
      def slot_two(self, slot, data:Tensor):
          self._2emb=data;
          self._distance();

      #-------------------------------------------------------------------------
      # SIGNALS
      #-------------------------------------------------------------------------
      @Block.signal("distance",float)
      def signal_distance(self, data:float):
          return data;

