from ..core import Block;

class Drain(Block):

      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          
      #-------------------------------------------------------------------------
      @Block.slot("drain", {object})
      def slot_image(self, slot, data):
          pass;


