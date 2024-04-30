# -*- coding: utf-8 -*-

import gc;
import gradio as gr
import numpy as np
import soundfile as sf
import librosa;
import requests;

# https://github.com/NeonGeckoCom/nsnet2-denoiser
from nsnet2_denoiser import NSnet2Enhancer;

from tqdm import tqdm;
from io import BytesIO;

from ...tools import tools;
from ...core  import Block;

class AudioSource(Block):

      def __init__(self, **kwargs):
          params, self._rest = tools.splitDict(["resample", "enhance", "vf"], **kwargs);
          super().__init__(**params);
          self._enhancer = NSnet2Enhancer(fs=self.context.default.AudioSampleRate);
          self._iface    = None;

      def _close(self):
          if self._iface is not None:
             self._iface.close();
             self._iface=None;
             gc.collect();

      def _process(self, audio):
          if audio is not None:
             sr, data = audio[0], np.array(audio[1]);
             if data.ndim == 2 and data.shape[1] == 2: data = np.mean(data, axis=1);
             data = data.astype(np.float32);
             data = data / np.max(np.abs(data));

             data = librosa.resample(data, orig_sr=sr, target_sr=self.context.default.AudioSampleRate, res_type=self.params.resample or "soxr_hq");

             if self.params.enhance or False:
                data = self._enhancer(data, self.context.default.AudioSampleRate);
                
             if self.params.vf is not None:
                factor=max(1,float(self.params.vf));
                data=data*factor;
             
             self.signal_audio(data);

             return data;

      @Block.slot("source",{str})
      def slot_source(self, slot, data):
          if data is not None:
             try:
                audio, sr = librosa.load(data, sr=self.context.default.AudioSampleRate);

             except Exception as e:
                try:
                  response = requests.get(data);
                  response.raise_for_status();
                  audio, sr = librosa.load(BytesIO(response.content), sr=self.context.default.AudioSampleRate)
                except Exception as second_exception:
                  raise;

             self._process( (sr, audio) ); 

      @Block.slot("launch",{object})
      def slot_launch(self, slot, data):
          self._close();
          self._iface = gr.Interface(fn=self._process,
                                     inputs=[
                                             gr.Audio(sources=["upload","microphone"],
                                                      type="numpy",
                                                      interactive=True,
                                                      format="mp3",
                                                      label="Graba o sube tu audio",
                                                      show_download_button=True,
                                                      show_share_button=False),
                                            ],
                                      outputs=None,
                                    );

          self._iface.launch(share=False, debug=False)

      @Block.slot("close", {object})
      def slot_close(self, slot, data):
          self._close();

      @Block.signal("audio", np.ndarray)
      def signal_audio(self, data):
          return data;

      def launch(self):
          self.context.emit(target=self, slot_name="launch", data=None);

      def source(self, file):
          self.context.emit(target=self, slot_name="source", data=file);
