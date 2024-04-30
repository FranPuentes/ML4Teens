# -*- coding: utf-8 -*-

import os;
import PIL;

from PIL.Image import Image;

from ultralytics import YOLO;

from ...core import Block;

class YoloPredict(Block):

      #--------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          self._nmodel=self.params.model;
          self._labels=self.params.labels;

          if self.params.files:
             self._nmodel=self.params.files["model"];

      #--------------------------------------------------------------------------
      @Block.slot("files",{dict})
      def slot_files(self, slot, data):
          if data:
             self._nmodel=data["model"];

      #--------------------------------------------------------------------------
      @Block.slot("model",{str})
      def slot_files(self, slot, data):
          if data:
             self._nmodel=data            

      #--------------------------------------------------------------------------
      @Block.slot("image",{Image})
      def slot_image(self, slot, data):
          model = YOLO(self._nmodel);
          try:
            results = model(data, stream=False, verbose=False);
            for r in results:
                if self.signal_image():
                   image = r.plot();
                   image = PIL.Image.fromarray(image[..., ::-1]);
                   assert isinstance(image, Image);
                   self.signal_image(image);          
          finally:
            del model;

      #--------------------------------------------------------------------------
      @Block.signal("image",Image)
      def signal_image(self, data):
          return data;

