# -*- coding: utf-8 -*-

from ...core  import Block;
from ...tools import tools;

class TfIdf(Block):

      def __init__(self, **kwargs):
          params, self._rest = tools.splitDict(["reset"], **kwargs);
          super().__init__(**params);
          self._reference=None;
          self._text     =None;

      def _calc(self):
          if self._reference is not None and self._text is not None:
             from sklearn.feature_extraction.text import TfidfVectorizer;
             from sklearn.metrics.pairwise import cosine_similarity;
             vectorizer = TfidfVectorizer();
             tfidf_matrix = vectorizer.fit_transform([self._reference, self._text]);
             cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0];
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

      @Block.signal("similarity", float)
      def signal_similarity(self, data):
          return data;
