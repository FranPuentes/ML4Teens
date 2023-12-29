import PIL;
import numpy as np;

from PIL.Image import Image;
from ultralytics import YOLO;
from ..core import Block;

class ObjectID(Block):
      """
      Recibe una imagen (slot 'frame' o 'image') en forma de tensor numpy o PIL.Image, y emite la misma imagen, pero con elementos identificados.
      URL: https://docs.ultralytics.com/modes/predict

      Parámetos del objeto:
      ---------------------
      'conf':    object confidence threshold for detection (float, 0.25)
      'iou':     intersection over union (IoU) threshold for NMS (float, 0.7)
      'device':  device to run on, i.e. cuda device=0/1/2/3 or device=cpu (None|str)
      'max_det': maximum number of detections per image (int, 300)
      'classes': filter results by class, i.e. classes=0, or classes=[0,2,3] (int|list[int])

      SLOTS:
      ------
      frame <- np.ndarray
      image <- PIL.Image

      SIGNALS:
      --------
      frame -> np.ndarray
      image -> PIL.Image
      boxes -> object
      """

      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          """
          Constructor: puede recibir varios parámetros opcionales.
          """
          super().__init__();

          self.model_name="yolov8n.pt";
          if "model_name" in kwargs:
              if kwargs["model_name"].lower() in ["nano",  "xs"]: self.model_name="yolov8n.pt";
              if kwargs["model_name"].lower() in ["small", "s" ]: self.model_name="yolov8s.pt";
              if kwargs["model_name"].lower() in ["medium","m" ]: self.model_name="yolov8m.pt";
              if kwargs["model_name"].lower() in ["large", "l" ]: self.model_name="yolov8l.pt";
              if kwargs["model_name"].lower() in ["xlarge","xl"]: self.model_name="yolov8x.pt";

          for key in ["conf","iou","device","max_det","classes"]:
              if key in kwargs: self._params[key]=kwargs[key];

          self._model = YOLO(self.model_name);

      #-------------------------------------------------------------------------
      def classes(self):
          return self._model.names;

      #-------------------------------------------------------------------------
      @Block.slot("frame", {np.ndarray}, required=2)
      def slot_frame(self, slot, data):
          results = self._model(data, stream=True, verbose=False, **self._params);
          for r in results:
              if self.signal_boxes(): self.signal_boxes(r.boxes);
              if self.signal_frame():
                 frame = r.plot();
                 self.signal_frame(frame);
          self.reset("frame");

      #-------------------------------------------------------------------------
      @Block.slot("image", {Image}, required=2)
      def slot_image(self, slot, data):
          results = self._model(data, stream=False, verbose=False, **self._params);
          for r in results:
              if self.signal_boxes(): self.signal_boxes(r.boxes);
              if self.signal_image():
                 image = r.plot();
                 self.signal_image(image);
          self.reset("image");

      #-------------------------------------------------------------------------
      @Block.signal("frame", np.ndarray)
      def signal_frame(self, data):
          return data;

      #-------------------------------------------------------------------------
      @Block.signal("image", Image)
      def signal_image(self, data):
          return data;

      #-------------------------------------------------------------------------
      @Block.signal("boxes", dict)
      def signal_boxes(self, data):
          """
          A Boxes dictionary containing the detection bounding boxes, classes and confidences.
          """
          boxes=[{"class":(int(r),self._model.names[int(r)]), "conf":float(c), "xywh":[int(_) for _ in p], "xyxy":[int(_) for _ in k]} for r,c,p,k in zip(data.cls,data.conf,data.xywh,data.xyxy)];
          return boxes;

      #-------------------------------------------------------------------------
      def run(self, **kwarg):
          raise RuntimeError("No tiene sentido invocar el método 'run' de un objeto de clase 'YOLO'.");

