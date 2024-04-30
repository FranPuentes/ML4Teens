# -*- coding: utf-8 -*-

from ..core import Block;

class Value(Block):

      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          self._data=None;

      @Block.slot("data", {object})
      def slot_data(self, slot, data):
          self._data=data if data is not None else self.params.default;
          self.signal_data(self._data);

      @Block.signal("data", object)
      def signal_data(self, data):
          return data;

      @property
      def data(self):
          return self._data;
