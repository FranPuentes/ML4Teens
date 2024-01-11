import PIL;
import torch;

from PIL.Image import Image;

from transformers import DPTImageProcessor, DPTForDepthEstimation;

import numpy as np;

from ml4teens.core import Block;

class DepthEstimation(Block):

      def __init__(self, **kwargs):
          super().__init__(**kwargs);

          self.processor = DPTImageProcessor.from_pretrained("Intel/dpt-large")
          self.model     = DPTForDepthEstimation.from_pretrained("Intel/dpt-large")

      #-------------------------------------------------------------------------
      @Block.slot("image", {Image})
      def slot_image(self, slot, data):
          inputs = self.processor(images=data, return_tensors="pt");

          with torch.no_grad():
              outputs = self.model(**inputs);
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

