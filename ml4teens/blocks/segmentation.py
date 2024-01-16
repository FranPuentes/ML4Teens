import PIL;
import numpy as np;

from PIL.Image import Image;
from ultralytics import YOLO;

from ..core import Block;

class Segmentation(Block):

      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__();
          
          self.model_name="yolov8n-seg.pt";
          if "model_name" in kwargs:
              if kwargs["model_name"].lower() in ["nano",  "xs"]: self.model_name="yolov8n-seg.pt";
              if kwargs["model_name"].lower() in ["small", "s" ]: self.model_name="yolov8s-seg.pt";
              if kwargs["model_name"].lower() in ["medium","m" ]: self.model_name="yolov8m-seg.pt";
              if kwargs["model_name"].lower() in ["large", "l" ]: self.model_name="yolov8l-seg.pt";
              if kwargs["model_name"].lower() in ["xlarge","xl"]: self.model_name="yolov8x-seg.pt";
              
          for key in ["conf","iou","device","max_det","classes"]:
              if key in kwargs: self.params[key]=kwargs[key];

          self._model = YOLO(self.model_name);

      #-------------------------------------------------------------------------
      def classes(self):
          return self._model.names;

      #-------------------------------------------------------------------------
      @Block.slot("image", {Image})
      def slot_not(self, slot, data):
          results = self._model(data, stream=False, verbose=False, **self.params);
          for r in results:
              if self.signal_mask():
                 zero = np.zeros((data.height, data.width, len(data.getbands())), dtype=np.uint8)
                 image = r.plot(conf=False, pil=False, img=zero, labels=False, boxes=False, masks=True, probs=False);
                 image = PIL.Image.fromarray(image[..., ::-1]);
                 self.signal_mask(image);
              if self.signal_image():
                 image = r.plot(conf=False, pil=False, img=None, labels=False, boxes=False, masks=True, probs=False);
                 image = PIL.Image.fromarray(image[..., ::-1]);
                 assert isinstance(image, Image);
                 self.signal_image(image);

      #-------------------------------------------------------------------------
      @Block.signal("mask", Image)
      def signal_mask(self, data):
          return data;

      #-------------------------------------------------------------------------
      @Block.signal("image", Image)
      def signal_image(self, data):
          return data;
