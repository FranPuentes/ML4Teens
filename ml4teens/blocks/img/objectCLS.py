import os;

import PIL;

from PIL.Image import Image;
from ultralytics import YOLO;

from ...core import Block;

class ObjectCLS(Block):
      """
      Recibe una imagen (slot 'frame' o 'image') en forma de PIL.Image, y emite la misma imagen, pero con los elementos identificados.
      URL: https://docs.ultralytics.com/modes/predict

      Parámetos del objeto:
      'conf':    object confidence threshold for detection (float, 0.25)
      'iou':     intersection over union (IoU) threshold for NMS (float, 0.7)
      'device':  device to run on, i.e. cuda device=0/1/2/3 or device=cpu (None|str)
      'max_det': maximum number of detections per image (int, 300)
      'classes': filter results by class, i.e. classes=0, or classes=[0,2,3] (int|list[int])

      SLOTS:
      image <- PIL.Image

      SIGNALS:
      image -> PIL.Image
      boxes -> object
      """

      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          """
          Constructor: puede recibir varios parámetros opcionales.
          """
          super().__init__();

          cwd = os.path.dirname(__file__);
          mwd = os.path.join(cwd, '../../models');
          fwd = os.path.join(cwd, '../../fonts');
          
          self.model_name="yolov8n-cls.pt";
          if "model_name" in kwargs:
              if kwargs["model_name"].lower() in ["nano",  "xs"]: self.model_name="yolov8n-cls.pt";
              if kwargs["model_name"].lower() in ["small", "s" ]: self.model_name="yolov8s-cls.pt";
              if kwargs["model_name"].lower() in ["medium","m" ]: self.model_name="yolov8m-cls.pt";
              if kwargs["model_name"].lower() in ["large", "l" ]: self.model_name="yolov8l-cls.pt";
              if kwargs["model_name"].lower() in ["xlarge","xl"]: self.model_name="yolov8x-cls.pt";
          
          # https://docs.ultralytics.com/es/modes/predict/#probs    
          for key in ["conf","device","classes"]:
              if key in kwargs: self.params[key]=kwargs[key];
 
          self._queue=[];
          self._model = YOLO(os.path.join(mwd,self.model_name));
          assert self._model is not None;

      #-------------------------------------------------------------------------
      @Block.slot("image", {Image})
      def slot_image(self, slot, data):
          if data is not None:
             self._queue=[];
             results = self._model(data, stream=False, verbose=False, **self.params);
             
             for r in results:
                 self._queue += [(r.names[id],float(conf)) for id, conf in zip(r.probs.top5, r.probs.top5conf)]                    
                 if self.signal_classes():
                    self.signal_classes([(r.names[id],float(conf)) for id, conf in zip(r.probs.top5, r.probs.top5conf)]);
                 if self.signal_image():
                    image = r.plot();
                    image = PIL.Image.fromarray(image[..., ::-1]);
                    self.signal_image(image);             
                    
             if self.signal_class():
                try:
                  self.signal_class(self._queue.pop(0));
                except:
                  self.signal_end(True);

      #-------------------------------------------------------------------------
      @Block.slot("next", {object})
      def slot_next(self, slot, data):
          try:
            self.signal_class(self._queue.pop(0));
          except:
            self.signal_end(True);
      
      #-------------------------------------------------------------------------
      @Block.signal("image", Image)
      def signal_image(self, data):
          return data;

      #-------------------------------------------------------------------------
      @Block.signal("classes", list)
      def signal_classes(self, data):
          return data;
          
      #-------------------------------------------------------------------------
      @Block.signal("class", list)
      def signal_class(self, data):
          return data;

      #-------------------------------------------------------------------------
      @Block.signal("end", list)
      def signal_end(self, data):
          return data;
