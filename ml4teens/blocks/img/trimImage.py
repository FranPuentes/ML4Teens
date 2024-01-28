from PIL.Image import Image;

from ...core import Block;

class TrimImage(Block):

      #-------------------------------------------------------------------------
      # x1,y1,x2,y2:float
      # n:int
      # conf:float
      # classes:list[str|int]
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          assert isinstance(self.params.x1,      (type(None),float));
          assert isinstance(self.params.y1,      (type(None),float));
          assert isinstance(self.params.x2,      (type(None),float));
          assert isinstance(self.params.y2,      (type(None),float));
          assert isinstance(self.params.n,       (type(None),int));
          assert isinstance(self.params.conf,    (type(None),float));
          assert isinstance(self.params.classes, (type(None),list,tuple));
          assert self.params.classes is None or all([type(c) in (int,str) for c in self.params.classes]);
          self._boxes=None;
          self._image=None;

      #-------------------------------------------------------------------------
      def _trim(self):
          boxes=self._boxes;
          image=self._image;
          if boxes is not None and image is not None:
             n=self.params.n or 1;
             for i,box in enumerate(boxes):
                 #if n is not None and i+1 > n: break;
                 x1=int(image.width *box[0]);
                 y1=int(image.height*box[1]);
                 x2=int(image.width *box[2]);
                 y2=int(image.height*box[3]);
                 img=image.crop( (x1,y1,x2,y2) );
                 self.signal_image(img);
          self._boxes=None;

      #-------------------------------------------------------------------------
      @Block.slot("box", {dict})
      def slot_boxes(self, slot, data):
      
          if data:

             conf   =self.params.conf;
             classes=self.params.classes;
             
             assert "xyxy"  in data and len(data["xyxy"])>=4;
             assert "trust" in data;
             assert "kind"  in data;
             
             if conf is not None and data["trust"]<conf:
                return;
             
             if classes is not None:
                for aclass in classes:
                    if type(aclass) is int and data["kind"][0]!=aclass:                 return;
                    if type(aclass) is str and data["kind"][1].lower()!=aclass.lower(): return;

             self._boxes=[data["xyxy"]];
             self._trim();

      #-------------------------------------------------------------------------
      @Block.slot("boxes", {tuple, list})
      def slot_boxes(self, slot, data):

          if len(data)>0:

             if   all([type(d) is float for d in data]) and len(data)>=4:
                  self._boxes=data;
                  self._trim();

             elif all([type(d) is int for d in data]) and len(data)>=4:
                  self._boxes=data;
                  self._trim();

             elif all([type(d) is dict for d in data]) and all([("xyxy" in d) for d in data]):
                  rt=[];
                  conf   =self.params.conf;
                  classes=self.params.classes;
                  for d in data:
                      
                      assert len(d["xyxy"])>=4;

                      if conf is not None:
                         if d["trust"]<conf: continue;

                      if classes is not None:
                         skip=False;
                         for aclass in classes:
                             if type(aclass) is int and d["kind"][0]!=aclass: skip=True;
                             if type(aclass) is str and d["kind"][1].lower()!=aclass.lower(): skip=True;
                         if skip: continue;

                      rt.append(d["xyxy"]);
                      
                  self._boxes=rt;
                  self._trim();

      #-------------------------------------------------------------------------
      @Block.slot("image", {Image})
      def slot_image(self, slot, data):
          self._image=data;
          x1=self.params.x1;
          y1=self.params.y1;
          x2=self.params.x2;
          y2=self.params.y2;
          if all([(d is not None) for d in [x1,y1,x2,y2]]):
             self._boxes=[(x1,y1,x2,y2)];
             self._trim();
          else:
             self._trim();

      #-------------------------------------------------------------------------
      @Block.signal("image", Image)
      def signal_image(self, data):
          return data;
