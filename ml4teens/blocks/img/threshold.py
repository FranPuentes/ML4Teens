from PIL.Image import Image;

from ...core import Block;

class Threshold(Block):

      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          self._image    =None;
          self._threshold=None;

      def threshold(self, img, thr):
          if img is not None and thr is not None:
             if isinstance(thr, int):
                img = img.convert('L');
                if thr>0: img = img.point(lambda p: 255 if p > abs(thr) else 0);
                if thr<0: img = img.point(lambda p: 255 if p < abs(thr) else 0);
                img = img.convert('1');
             else:    
                assert isinstance(thr, (tuple,list)) and len(thr)==2;
                img = img.convert('L');
                img = img.point(lambda p: 0 if (p < thr[0] or p > thr[1]) else 255);
                img = img.convert('1');                 
             self.signal_image(img);
             return True;
          return False; 
          
      #-------------------------------------------------------------------------
      # SLOTS
      #-------------------------------------------------------------------------
      @Block.slot("image",{Image})
      def slot_image(self, slot, data):
          self._image=data;
          if self.threshold(self._image, self._threshold if self._threshold is not None else self.params.cut):
             if self.params.clear:
                self._image=None;
             if self.params.clearAll:
                self._image=None;
                self._threshold=None;

      @Block.slot("threshold",{int,tuple,list,range})
      def slot_threshold(self, slot, data):
          self._threshold=data;
          if self.threshold(self._image, self._threshold if self._threshold is not None else self.params.cut):
             if self.params.clear:
                self._threshold=None;
             if self.params.clearAll:
                self._image=None;
                self._threshold=None;

      #-------------------------------------------------------------------------
      # SIGNALS
      #-------------------------------------------------------------------------
      @Block.signal("image",Image)
      def signal_image(self, data):
          return data;

