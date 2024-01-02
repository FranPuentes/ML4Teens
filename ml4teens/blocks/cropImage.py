from PIL.Image import Image;

from ..core import Block;

class CropImage(Block):

      #-------------------------------------------------------------------------
      # x1,y1,x2,y2:float
      # n:int
      # conf:float
      # classes:list[str|int]
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          assert "x1"      not in self._params or type(self._params["x1"     ]) is float;
          assert "y1"      not in self._params or type(self._params["y1"     ]) is float;
          assert "x2"      not in self._params or type(self._params["x2"     ]) is float;
          assert "y2"      not in self._params or type(self._params["y2"     ]) is float;          
          assert "n"       not in self._params or type(self._params["n"      ]) in [int];
          assert "conf"    not in self._params or type(self._params["conf"   ]) in [float];
          assert "classes" not in self._params or (type(self._params["classes"]) is list and all([type(c) in [int,str] for c in self._params["classes"]]));

      #-------------------------------------------------------------------------
      def _crop(self):
          if self.rightValue("boxes") and self.rightValue("image"):
             n=self._param("n");
             boxes=self._values["boxes"];
             image=self._values["image"];
             for i,box in enumerate(boxes):
                 if n is not None and i+1 > n: break;
                 x1=int(image.width *box[0]);
                 y1=int(image.height*box[1]);
                 x2=int(image.width *box[2]);
                 y2=int(image.height*box[3]);
                 img=image.crop( (x1,y1,x2,y2) );
                 self.signal_image(img);
             self.reset("boxes","image"); 

      #-------------------------------------------------------------------------
      @Block.slot("boxes", {tuple, list}, required=3)
      def slot_boxes(self, slot, data):

          if len(data)>0:

             if   all([type(d) is float for d in data]) and len(data)>=4:
                  self._values[slot]=[data];
                  self._crop();

             elif all([type(d) is int for d in data]) and len(data)>=4:
                  self._values[slot]=[data];
                  self._crop();

             elif all([type(d) is dict for d in data]) and all([("xyxy" in d) for d in data]):
                  rt=[];
                  conf   =self._param("conf");
                  classes=self._param("classes");
                  for d in data:
                      
                      assert len(d["xyxy"])>=4;

                      if conf is not None:
                         if d["conf"]<conf: continue;

                      if classes is not None:
                         skip=False;
                         for aclass in classes:
                             if type(aclass) is int and d["class"][0]!=aclass: skip=True;
                             if type(aclass) is str and d["class"][1].lower()!=aclass.lower(): skip=True;
                         if skip: continue;

                      rt.append(d["xyxy"]);
                  self._values[slot]=rt;
                  self._crop();

      #-------------------------------------------------------------------------
      @Block.slot("image", {Image}, required=3)
      def slot_image(self, slot, data):
          x1=self._param("x1");
          y1=self._param("y1");
          x2=self._param("x2");
          y2=self._param("y2");
          if all([(d is not None) for d in [x1,y1,x2,y2]]):
             self.setValue("boxes",[(x1,y1,x2,y2)]);
             self._crop();
          else:
             self._crop();

      #-------------------------------------------------------------------------
      @Block.signal("image", Image)
      def signal_image(self, data):
          return data;

      #-------------------------------------------------------------------------
      def run(self, **kwarg):
          raise RuntimeError("No tiene sentido invocar el método 'run' de un objeto de clase 'CropImage'.");

