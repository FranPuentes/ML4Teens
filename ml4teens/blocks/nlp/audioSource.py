import gc;
import gradio as gr
import numpy as np
import soundfile as sf
import librosa;
import requests;
from io import BytesIO;

#from resemble_enhance.enhancer.inference import denoise, enhance;

from ...tools import tools;
from ...core  import Block;

class AudioSource(Block):

      def __init__(self, **kwargs):
          params, self._rest = tools.splitDict(["resample", "denoise", "enhance"], **kwargs);
          super().__init__(**params);
          self._iface=None;

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

             #if self.params.denoise or self.params.enhance:
             #   denoising=False;
             #   nfe=64;            # range(1, 128+1, 1)
             #   solver="Midpoint"; # ["Midpoint", "RK4", "Euler"]
             #   tau=0.5;           # range(0, 1, 0.01)
             #   device="cpu"; #self.context.default.device;
             #   if self.params.denoise: data, sr = denoise(data, sr, device);
             #   if self.params.enhance: data, sr = enhance(data, sr, device, nfe=nfe, solver=solver, lambd=0.9 if denoising else 0.1, tau=tau);

             data = librosa.resample(data, orig_sr=sr, target_sr=self.context.default.AudioSampleRate, res_type=self.params.resample or "soxr_hq");

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
