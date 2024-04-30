# -*- coding: utf-8 -*-

import PIL;
import torch;

from PIL.Image import Image;


import numpy as np;

from ...core import Block;

class DepthEstimation(Block):

      processor=None;
      model    =None;

      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          
          from transformers import AutoImageProcessor, AutoModelForDepthEstimation;
          #from transformers import DPTImageProcessor, DPTForDepthEstimation;
          #from transformers import pipeline;
          
          #self.processor = DPTImageProcessor.from_pretrained("Intel/dpt-large")
          #self.model     = DPTForDepthEstimation.from_pretrained("Intel/dpt-large")
          #self._pipeline = pipeline("depth-estimation",model="vinvino02/glpn-nyu");
          
          if DepthEstimation.processor is None or DepthEstimation.model is None:
             DepthEstimation.processor = AutoImageProcessor.from_pretrained("LiheYoung/depth-anything-base-hf");
             DepthEstimation.model     = AutoModelForDepthEstimation.from_pretrained("LiheYoung/depth-anything-base-hf");

      #-------------------------------------------------------------------------
      @Block.slot("image", {Image})
      def slot_image(self, slot, data):

          if data:
             #predictions=self._pipeline(data);
             #imagen=predictions["depth"];

             inputs = DepthEstimation.processor(images=data, return_tensors="pt");
             
             with torch.no_grad():
                  outputs = DepthEstimation.model(**inputs);
                  predicted_depth = outputs.predicted_depth;
             
             prediction = torch.nn.functional.interpolate(predicted_depth.unsqueeze(1), size=data.size[::-1], mode="bicubic", align_corners=False);
             
             output = prediction.squeeze().cpu().numpy();
             formatted = (output * 255 / np.max(output)).astype("uint8");
             imagen = PIL.Image.fromarray(formatted);

             self.signal_image(imagen);

      #-------------------------------------------------------------------------
      @Block.signal("image", Image)
      def signal_image(self, data):
          return data;

