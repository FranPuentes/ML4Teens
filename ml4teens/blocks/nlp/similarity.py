# -*- coding: utf-8 -*-

import numpy as np;
import torch;

from ...core  import Block;
from ...tools import tools;

class Similarity(Block):

      def __init__(self, **kwargs):
          params, self._rest = tools.splitDict(["reset"], **kwargs);
          super().__init__(**params);
          self._tokenizer=None;
          self._model    =None;
          self._reference=None;
          self._text     =None;

      def _load(self):
          from transformers import AutoTokenizer, AutoModel;
          if self._tokenizer is None:
             self._tokenizer = AutoTokenizer.from_pretrained("intfloat/multilingual-e5-large");
          if self._model is None:
             self._model = AutoModel.from_pretrained("intfloat/multilingual-e5-large");
             self._model = torch.quantization.quantize_dynamic(self._model, {torch.nn.Linear}, dtype=torch.qint8);

      def _embedding(self, text):
          self._load();
          inputs = self._tokenizer(text, return_tensors="pt", padding=True, truncation=True);
          with torch.no_grad():
               outputs = self._model(**inputs);
          return outputs.last_hidden_state.mean(dim=1).squeeze();

      def _calc(self):
          if self._reference is not None and self._text is not None:

             def normalize(v):
                 norm = np.linalg.norm(v);
                 if norm == 0: return v;
                 else:         return v / norm;

             def cosine_similarity(vector1, vector2):
                 vector1 = np.array(vector1);
                 vector2 = np.array(vector2);
                 dot_product = np.dot(vector1, vector2);
                 return dot_product;

             emb1=normalize(self._embedding(self._reference));
             emb2=normalize(self._embedding(self._text     ));
             cosine_sim=cosine_similarity(emb1, emb2);
             self.signal_similarity(cosine_sim);
             return True;
          else:
             return False;

      @Block.slot("reference", {str})
      def slot_reference(self, slot, data):
          if data and isinstance(data,str):
             self._reference=data;
             rt=self._calc();
             if rt and self.params.reset: self._reference=None;
             return rt;

      @Block.slot("text", {str})
      def slot_text(self, slot, data):
          if data and isinstance(data,str):
             self._text=data;
             rt=self._calc();
             if rt and self.params.reset: self._text=None;
             return rt;

      @Block.slot("end", {object})
      def slot_end(self, slot, data):
          self._tokenizer=None;
          self._model    =None;

      @Block.signal("similarity", float)
      def signal_similarity(self, data):
          return data;
