import PIL;

from PIL.Image import Image;

from transformers import BlipProcessor, BlipForConditionalGeneration;

from ...core import Block;

class ImageToText(Block):

      def __init__(self, **kwargs):
          super().__init__();

          self.model_name="Salesforce/blip-image-captioning-base";
          if "model_name" in kwargs:
             if kwargs["model_name"].lower() in ["small", "s" ]: self.model_name="Salesforce/blip-image-captioning-base";
             if kwargs["model_name"].lower() in ["base",  "b" ]: self.model_name="Salesforce/blip-image-captioning-base";
             if kwargs["model_name"].lower() in ["large", "l" ]: self.model_name="Salesforce/blip-image-captioning-large";

          for key in ["caption"]:
              if key in kwargs:
                 self.params[key]=kwargs[key];  

          self.processor = BlipProcessor.from_pretrained(self.model_name);
          self.model     = BlipForConditionalGeneration.from_pretrained(self.model_name);

      #-------------------------------------------------------------------------
      @Block.slot("caption", {str})
      def slot_caption(self, slot, data):
          pass;

      #-------------------------------------------------------------------------
      @Block.slot("image", {Image})
      def slot_image(self, slot, data):
          
          caption=self.params.caption or self.token["caption"].data;

          if caption:
             inputs = self.processor(data, caption, return_tensors="pt");
             out = self.model.generate(max_new_tokens=self.params.maxNewTokens or 128, **inputs);
             self.signal_text(self.processor.decode(out[0], skip_special_tokens=True));
          else:
             inputs = self.processor(data, return_tensors="pt");
             out = self.model.generate(max_new_tokens=self.params.maxNewTokens or 128, **inputs);
             self.signal_text(self.processor.decode(out[0], skip_special_tokens=True));

      #-------------------------------------------------------------------------
      @Block.signal("text", str)
      def signal_text(self, data):
          return data;

