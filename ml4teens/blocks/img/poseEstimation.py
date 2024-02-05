import os;

import PIL;

from PIL.Image import Image;

from ultralytics import YOLO;

from ...core import Block;

class PoseEstimation(Block):

      def __init__(self, **kwargs):
          super().__init__();
          
          cwd = os.path.dirname(__file__);
          mwd = os.path.join(cwd, '../../models');
          fwd = os.path.join(cwd, '../../fonts');
          
          self.model_name="yolov8n-pose.pt";
          if "model_name" in kwargs:
              if kwargs["model_name"].lower() in ["nano",  "xs"]: self.model_name="yolov8n-pose.pt";
              if kwargs["model_name"].lower() in ["small", "s" ]: self.model_name="yolov8s-pose.pt";
              if kwargs["model_name"].lower() in ["medium","m" ]: self.model_name="yolov8m-pose.pt";
              if kwargs["model_name"].lower() in ["large", "l" ]: self.model_name="yolov8l-pose.pt";
              if kwargs["model_name"].lower() in ["xlarge","xl"]: self.model_name="yolov8x-pose.pt";
          
          self._n=kwargs.pop("n",None);
          assert (type(self._n) is int and self._n >= 0) or self._n is None, "El parámetro 'n' debe ser un número entero>=0 o no aparecer";

          for key in ["conf","iou","device","max_det","classes"]:
              if key in kwargs: self.params[key]=kwargs[key];

          self._model = YOLO(os.path.join(mwd, self.model_name));
          assert self._model is not None;

      #-------------------------------------------------------------------------
      @Block.slot("image", {Image})
      def slot_image(self, slot, data):
          if data is not None:
             results = self._model.predict(data, stream=False, verbose=False, **self.params);
             for r in results:
                 if self.signal_boxes():
                    self.signal_boxes((r.boxes,r.keypoints));
                 if self.signal_image():
                    image = r.plot(conf=False, labels=False, boxes=False, masks=False, probs=False);
                    image = PIL.Image.fromarray(image[..., ::-1]);
                    self.signal_image(image);

      #-------------------------------------------------------------------------
      @Block.signal("image", Image)
      def signal_image(self, data):
          return data;
          
      #-------------------------------------------------------------------------
      @Block.signal("boxes", list)
      def signal_boxes(self, data):
          
          _boxes, _keypoints = data;
          
          boxes=[{
                  "kind":(int(r),self._model.names[int(r)]),
                  "trust":float(c),
                  "xyxy":[float(_) for _ in k],
                  "kp":[[float(_) for _ in l] for l in p],
                 }
                 for r,c,k,p in zip(_boxes.cls,_boxes.conf,_boxes.xyxyn,_keypoints.xyn)];

          if self._n: return boxes[:self._n];
          else:       return boxes;
