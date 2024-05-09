# -*- coding: utf-8 -*-

import os;
import math;
import torch;

import PIL;

from PIL.Image import Image;

import numpy as np;

from ultralytics import YOLO;

from ...tools import tools;
from ...core  import Block;

class PoseEstimation(Block):

      def __init__(self, **kwargs):
          params, self._rest = tools.splitDict(["model","n","bodies","verge"], **kwargs);
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

                 if result.boxes is not None and result.keypoints.conf is not None and result.keypoints.xyn is not None:

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
                       for conf,xyn in zip(result.keypoints.conf.cpu(), result.keypoints.xyn.cpu()):
                           cv=[];
                           mc = torch.mean(xyn, dim=0);
                           for i, point in enumerate(xyn):
                               if conf[i] >= (self.params.verge or 0.5):
                                  d=math.sqrt((point[0]-mc[0])**2 + (point[1]-mc[1])**2);
                                  cv.append(d);
                               else:
                                  cv.append(None);                               
                          
                           cv = np.array(cv, dtype=float);
                           mean_value = np.nanmean(cv);
                           mask=np.isnan(cv);
                           cv[mask] = mean_value;
                           cv = cv /  np.linalg.norm(cv);
                           cv[mask] = np.nan;
                          
                           self.signal_features(cv); 
                       
                    if self.signal_image():
                       image = result.plot(conf=False, labels=False, boxes=False, masks=False, probs=False);
                       image = PIL.Image.fromarray(image[..., ::-1]);
                       self.signal_image(image);

      #-------------------------------------------------------------------------
      @Block.signal("image", Image)
      def signal_image(self, data):
          return data;
          
      #-------------------------------------------------------------------------
      @Block.signal("features", np.ndarray)
      def signal_features(self, data):
          return data;

      #-------------------------------------------------------------------------
      @Block.signal("boxes", list)
      def signal_boxes(self, data):
          return data;
