# -*- coding: utf-8 -*-

import os;

import PIL;

from PIL.Image import Image;

from ultralytics import YOLO;

from ...tools import tools;
from ...core  import Block;

class PoseEstimation(Block):

      def __init__(self, **kwargs):
          params, self._rest = tools.splitDict(["model","n","bodies"], **kwargs);
          super().__init__(**params);
          
          cwd = os.path.dirname(__file__);
          mwd = os.path.join(cwd, '../../models');
          fwd = os.path.join(cwd, '../../fonts');
          
          self.model_name="yolov8n-pose.pt";
          if self.params.model in ["nano",  "xs"]: self.model_name="yolov8n-pose.pt";
          if self.params.model in ["small", "s" ]: self.model_name="yolov8s-pose.pt";
          if self.params.model in ["medium","m" ]: self.model_name="yolov8m-pose.pt";
          if self.params.model in ["large", "l" ]: self.model_name="yolov8l-pose.pt";
          if self.params.model in ["xlarge","xl"]: self.model_name="yolov8x-pose.pt";
          
          _n=self.params.n or self.params.bodies or None;
          assert (type(_n) is int and _n >= 0) or _n is None, "El parámetro 'n' (o 'bodies') debe ser un número entero >= 0";
          self._rest["max_det"]=_n;

          self._model = YOLO(os.path.join(mwd, self.model_name));
          assert self._model is not None, f"No he podido carga el modelo '{self.model_name}'";

      #-------------------------------------------------------------------------
      @Block.slot("image", {Image})
      def slot_image(self, slot, data):
          if data is not None:
             results = self._model.predict(data, verbose=False, **self._rest);
             for result in results:
                 if self.signal_boxes():
                                  
                    _boxes     = result.boxes;
                    _keypoints = result.keypoints;
                    
                    boxes=[{
                            "kind":(int(r),self._model.names[int(r)]),
                            "trust":float(c),
                            "xyxy":[float(_) for _ in k],
                            "kp":[[float(_) for _ in l] for l in p],
                           }
                           for r,c,k,p in zip(_boxes.cls,_boxes.conf,_boxes.xyxyn,_keypoints.xyn)];

                    self.signal_boxes(boxes);
                    
                 if self.signal_features():
                    pass;
                    
                 if self.signal_image():
                    image = r.plot(conf=False, labels=False, boxes=False, masks=False, probs=False);
                    image = PIL.Image.fromarray(image[..., ::-1]);
                    self.signal_image(image);

      #-------------------------------------------------------------------------
      @Block.signal("image", Image)
      def signal_image(self, data):
          return data;
          
      #-------------------------------------------------------------------------
      @Block.signal("features", list)
      def signal_features(self, data):
          return data;

      #-------------------------------------------------------------------------
      @Block.signal("boxes", list)
      def signal_boxes(self, data):
          return data;
