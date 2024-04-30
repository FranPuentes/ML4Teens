# -*- coding: utf-8 -*-

import gc;
import torch;
import numpy as np;
import torch;
import librosa;

from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline;

from ...tools import tools;
from ...core  import Block;

class Transcribe(Block):

      @staticmethod
      def models():
          return ["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"];

      def __init__(self, **kwargs):
          params, self._rest = tools.splitDict(["model", "language"], **kwargs);
          super().__init__(**params);
          self._language=self.params.language or "es";
          torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32;
          if self.params.model: model_id=f"openai/whisper-{self.params.model}";
          else:                 model_id= "openai/whisper-medium";
          model     = AutoModelForSpeechSeq2Seq.from_pretrained(model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True).to(self.context.device);
          processor = AutoProcessor.from_pretrained(model_id);
          self._pipe = pipeline("automatic-speech-recognition",
                                model=model,
                                tokenizer=processor.tokenizer,
                                feature_extractor=processor.feature_extractor,
                                max_new_tokens=128,
                                chunk_length_s=30,
                                batch_size=16,
                                return_timestamps=True,
                                torch_dtype=torch_dtype,
                                device=self.context.device,
                               );

      @Block.slot("source",{str})
      def slot_source(self, slot, data):
          if data is not None:
             result = self._pipe(data, generate_kwargs={"language": self._language});
             self.signal_text(result["text"]);
             if self.signal_segments():
                chunks=[];
                for chunk in result["chunks"]:
                    chunks.append({"timestamp":chunk["timestamp"], "text":chunk["text"].strip()});
                self.signal_segments(chunks);

      @Block.slot("audio",{np.ndarray})
      def slot_audio(self, slot, data):
          if data is not None and data.size > 0:
             data = librosa.resample(data, orig_sr=self.context.default.AudioSampleRate, target_sr=16000, res_type=self.params.resample or "soxr_hq");
             result = self._pipe(data, generate_kwargs={"language": self._language});
             self.signal_text(result["text"]);
             if self.signal_segments():
                chunks=[];
                for chunk in result["chunks"]:
                    chunks.append({"timestamp":chunk["timestamp"], "text":chunk["text"].strip()});
                self.signal_segments(chunks);

      @Block.slot("close", {object})
      def slot_close(self, slot, data):
          self._model=None;
          gc.collect();
          torch.cuda.empty_cache();

      @Block.signal("text", str)
      def signal_text(self, data):
          return data;

      @Block.signal("segments", list)
      def signal_segments(self, data):
          return data;

      def source(self, data):
          """
          Envía una señal al bloque al que pertenece, al slot 'source' con el dato que se le pasa como parámetro.
          El parámetro debe ser el nombre de un fichero de tipo audio (mp3, wav).
          """
          self.context.emit(target=self, slot_name="source", data=data);
