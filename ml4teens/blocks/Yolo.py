from ultralytics import YOLO;
from PIL import Image;

from ..core import Block;

#https://github.com/ultralytics/ultralytics?tab=readme-ov-file

"""
TODO
----
conf  	      float	0.25	object confidence threshold for detection
iou	      float	0.7	intersection over union (IoU) threshold for NMS
imgsz 	      int or tuple	640	image size as scalar or (h, w) list, i.e. (640, 480)
half  	      bool	False	use half precision (FP16)
max_det	      int	300	maximum number of detections per image
vid_stride	  bool	False	video frame-rate stride
stream_buffer	bool	False	buffer all streaming frames (True) or return the most recent frame (False)
classes	      list[int]	None	filter results by class, i.e. classes=0, or classes=[0,2,3]

Opciones
--------
Imagen y/o json con las identificaciones
"""

class Yolo(Block):
      """
      Los bloques Yolo llevan a cabo tareas de percepción en imágenes.
      * Identifiación de objetos
      * Segmentación
      * Determinación de poses.

      Modelos
      =======

      Model	  Params FLOPs
      -----   ------ -----
      yolov8n	3.2	   8.7
      yolov8s	11.2	 28.6
      yolov8m	25.9	 78.9
      yolov8l	43.7	 165.2
      yolov8x	68.2	 257.8

      Señales
      =======
      * frame - emite una señal de tipo Tensor (numpy.ndarray)

      Slots
      =====
      * frame - recibe una señal de tipo Tensor (numpy.ndarray)
      """

      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          model_name="yolov8n.pt";
          if "model" in kwargs: model_name=kwargs["model"];
          self._model = YOLO(model_name);

      #-------------------------------------------------------------------------
      @Block.slot("frame", {np.ndarray}, required=True)
      def slot_frame(self, slot, data):
          results = self._model(data, stream=True, verbose=False);
          for r in results:
              frame = r.plot();
              self.signal_frame(frame);
          self.reset("frame");

      #-------------------------------------------------------------------------
      @Block.signal("frame", np.ndarray)
      def signal_frame(self, data):
          return data;

      #-------------------------------------------------------------------------
      def run(self, **kwarg):
          raise RuntimeError("No tiene sentido invocar el método 'run' de un objeto de clase 'YOLO'.");