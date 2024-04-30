# -*- coding: utf-8 -*-

from ..core import Block;

class Values(Block):

      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          self._data=[];

      @Block.slot("data", {object})
      def slot_data(self, slot, data):
          self._data.append(data if data is not None else self.params.default);
          self.signal_data(data);

      @Block.signal("data", object)
      def signal_data(self, data):
          return data;

      @property
      def data(self):
          return self._data;
