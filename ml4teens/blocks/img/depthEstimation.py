# -*- coding: utf-8 -*-

import PIL;
import torch;

from PIL.Image import Image;

import matplotlib.pyplot as plt;
from matplotlib.colors import Normalize;

import numpy as np;

from ...core import Block;

class DepthEstimation(Block):

      processor=None;
      model    =None;

      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          
          from transformers import AutoImageProcessor, AutoModelForDepthEstimation;
          
          #checkpoint = self.params.model or ""Intel/dpt-large";
          #checkpoint = self.params.model or "vinvino02/glpn-nyu";
          checkpoint = self.params.model or "LiheYoung/depth-anything-base-hf";
          
          if DepthEstimation.processor is None or DepthEstimation.model is None:
             DepthEstimation.processor = AutoImageProcessor.from_pretrained         (checkpoint, device=self.context.device);
             DepthEstimation.model     = AutoModelForDepthEstimation.from_pretrained(checkpoint).to(self.context.device);

      #-------------------------------------------------------------------------
      @Block.slot("image", {Image})
      def slot_image(self, slot, data):

          if data:

             inputs = DepthEstimation.processor(images=data, return_tensors="pt").to(self.context.device);
             
             with torch.no_grad():
                  outputs = DepthEstimation.model(**inputs);
                  predicted_depth = outputs.predicted_depth;
             
             prediction = torch.nn.functional.interpolate(predicted_depth.unsqueeze(1), size=data.size[::-1], mode="bicubic", align_corners=False);
             
             output = prediction.squeeze().cpu().numpy();
             if self.params.colormap:
                normalized = Normalize(vmin=np.min(output), vmax=np.max(output))(output);
                colored    = plt.get_cmap(self.params.colormap)(normalized);
                rgb        = (colored[..., :3] * 255).astype(np.uint8);
                imagen     = PIL.Image.fromarray(rgb);
             else:   
                formatted  = ( 255 * (output-np.min(output)) / (np.max(output)-np.min(output)) ).astype(np.uint8);
                imagen     = PIL.Image.fromarray(formatted);

             self.signal_image(imagen);

      #-------------------------------------------------------------------------
      @Block.signal("image", Image)
      def signal_image(self, data):
          return data;

