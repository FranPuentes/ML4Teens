import os;
import numpy as np;
import PIL;
import cv2;

from ultralytics import YOLO;

from PIL.Image import Image;

# https://learnopencv.com/deep-learning-based-object-detection-using-yolov3-with-opencv-python-c/

from ...core import Block;

#===============================================================================
class FaceBoxing(Block):

      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);

          cwd = os.path.dirname(__file__);
          mwd = os.path.join(cwd, '../../models');
          fwd = os.path.join(cwd, '../../fonts');
          
          self._model = YOLO(os.path.join(mwd, "yolov8n-faces.pt"));
               
          self._font = PIL.ImageFont.truetype(os.path.join(fwd, self.params.fontname or "Roboto-Bold.ttf"), self.params.fontsize or 12);

          self._queue=[];

      #-------------------------------------------------------------------------
      # SLOTS
      #-------------------------------------------------------------------------
      @Block.slot("image", {Image})
      def slot_image(self, slot, data):
      
          if self.params.clear:
             self._queue.clear();
          
          if data and isinstance(data, Image):
             
             width, height = data.width, data.height;
              
             results = self._model(data, stream=False, verbose=False);
              
             rt=[];
              
             for r in results:
                 #print(r.keypoints); # TODO falta la conf de los puntos
                 boxes=[{
                         "kind" : (int(r),self._model.names[int(r)]),
                         "trust": float(c),
                         "xyxy" : [float(_) for _ in k],
                         "xy"   : [[float(_) for _ in l]  for l in p],
                        }
                        for r,c,k,p in zip(r.boxes.cls, r.boxes.conf, r.boxes.xyxyn, r.keypoints.xyn)];
                 
                 self._queue += boxes;
                
             if self.signal_boxes():
                         
                if self.params.n: self.signal_boxes(boxes[:self.params.n]);
                else:             self.signal_boxes(boxes                );
                 
             if self.signal_box():
                try:
                  box=self._queue.pop(0);
                  self.signal_box(box);
                except IndexError:
                  self.signal_end(True);
                 
             if self.signal_image():
                salida=data.copy();
                imageDraw=PIL.ImageDraw.Draw(salida);
                for label, conf, xyxyn, xyn in zip(r.boxes.cls, r.boxes.conf, r.boxes.xyxyn, r.keypoints.xyn):
                 
                    label="face";
                    x1 = xyxyn[0];
                    y1 = xyxyn[1];
                    x2 = xyxyn[2];
                    y2 = xyxyn[3];
                     
                    if self.params.drawAll or self.params.drawBoxes or self.params.drawBox:
                       imageDraw.rectangle(((int(x1*width), int(y1*height), int(x2*width), int(y2*height))), fill=None, outline=(self.params.color or "red"), width=(self.params.width or 1));
                        
                    if self.params.drawAll or self.params.drawText:
                       texto=f"{label} ({round(float(conf),3)})";
                       alto_texto = (self.params.fontsize or 12);
                       imageDraw.text((int(x1*width), int(y1*height)-int(alto_texto)-2), texto, fill=self.params.fontcolor or (0, 0, 0), font=self._font);
                     
                    if self.params.drawAll or self.params.drawLandmarks or self.params.drawPoints:
                       for x, y in xyn:
                           if x and y:
                              x = float(x)*width;
                              y = float(y)*height;
                              d = self.params.pointsize or 2;
                              imageDraw.rectangle(((int(x)-d, int(y)-d, int(x)+d, int(y)+d)), fill=self.params.pointcolor or (0, 0, 0), width=0);
                     
                self.signal_image(salida);
             
      #-------------------------------------------------------------------------
      @Block.slot("next", {object})
      def slot_next(self, slot, data):
          try:
            box=self._queue.pop(0);
            self.signal_box(box);
          except IndexError:
            self.signal_box(None);
          
      #-------------------------------------------------------------------------
      # SIGNALS
      #-------------------------------------------------------------------------
      @Block.signal("image", Image)
      def signal_image(self, data):
          return data;

      #-------------------------------------------------------------------------
      @Block.signal("box", dict)
      def signal_box(self, data):
          return data;
          
      #-------------------------------------------------------------------------
      @Block.signal("boxes", list)
      def signal_boxes(self, data):
          return data;

      #-------------------------------------------------------------------------
      @Block.signal("end", bool)
      def signal_end(self, data):
          return bool(data);
          