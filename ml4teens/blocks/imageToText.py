import PIL;

from PIL.Image import Image;

from transformers import BlipProcessor, BlipForConditionalGeneration;

from ..core import Block;

class ImageToText(Block):

      def __init__(self, **kwargs):
          super().__init__(**kwargs);

          self.model_name="Salesforce/blip-image-captioning-base";
          if "model_name" in kwargs:
             if kwargs["model_name"].lower() in ["small", "s" ]: self.model_name="Salesforce/blip-image-captioning-base";
             if kwargs["model_name"].lower() in ["base",  "b" ]: self.model_name="Salesforce/blip-image-captioning-base";
             if kwargs["model_name"].lower() in ["large", "l" ]: self.model_name="Salesforce/blip-image-captioning-large";

          self._params={ };
          for key in ["caption"]:
              if key in kwargs: self._params[key]=kwargs[key];  

          self.processor = BlipProcessor.from_pretrained(self.model_name);
          self.model     = BlipForConditionalGeneration.from_pretrained(self.model_name);

      #-------------------------------------------------------------------------
      @Block.slot("caption", {str}, required=False)
      def slot_caption(self, slot, data):
          pass;

      #-------------------------------------------------------------------------
      @Block.slot("image", {Image}, required=True)
      def slot_image(self, slot, data):
          
          caption=self._param("caption") or self.getValue("caption");

          if caption:
             inputs = self.processor(data, caption, return_tensors="pt");
             out = self.model.generate(**inputs);
             self.signal_text(self.processor.decode(out[0], skip_special_tokens=True));
          else:
             inputs = self.processor(data, return_tensors="pt");
             out = self.model.generate(**inputs);
             self.signal_text(self.processor.decode(out[0], skip_special_tokens=True));

      #-------------------------------------------------------------------------
      @Block.signal("text", str)
      def signal_text(self, data):
          return data;

