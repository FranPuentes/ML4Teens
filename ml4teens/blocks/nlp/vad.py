import numpy as np;
import math;
import webrtcvad;
import torch;
import torchaudio;

from jupyter_ui_poll import ui_events;

from ...tools import tools;
from ...core  import Context;
from ...core  import Block;

class VAD(Block):
      """
      Recibe audios y los segmenta según espacios sin voz. Para cada segmento obtenido manda un mensaje síncrono.
      También envía el patrón actividad/silencio que ha detectado en forma de string.

      Limitaciones: Necesita de un denoising y un enhancer. El mínimo ruído lo confunde.

      Parámetros
      ==========

      **aggressiveness**: "agresividad" del algoritmo de VAD (*voice activity detection*), valores de 0 a 3 (por defecto 2).

      **silence**:  tiempo (en segundos o fracción) mínimo de silencio para considerar que estamos ante un final de sentencia.

      **patience**: tiempo (en segundos o fracción) mínimo activado para considerar que hay voz.
      """

      def __init__(self, **kwargs):
          params, self._rest = tools.splitDict(["aggressiveness","silence","patience"], **kwargs);
          super().__init__(**params);
          self._chunkTime  = self.context.default.VadChunkTime;
          self._sampleRate = self.context.default.AudioSampleRate;
          self._chunkSize  = int(self._sampleRate*self._chunkTime/1000);
          self._vad        = webrtcvad.Vad(self.params.aggressiveness or 2);
          self._silence    = math.ceil((self.params.silence  or 0.75)/(self.context.default.VadChunkTime/1000));
          self._patience   = math.ceil((self.params.patience or 5.00)/(self.context.default.VadChunkTime/1000))*self._chunkSize;
          self._buffer     = np.ndarray(0, dtype=np.int16);
          self._pattern    = list();
          self._s          = 0;
          self._c          = 0;

      def generate_tone(self, note, octave, duration):
          sr = self.context.default.AudioSampleRate;
          a4_freq, tones_from_a4 = 440, 12 * (octave - 4) + (note - 9);
          frequency = a4_freq * 2 ** (tones_from_a4 / 12);
          duration = int(duration);
          audio = np.linspace(0, duration, duration * sr);
          audio = (20000 * np.sin(audio * (2 * np.pi * frequency))).astype(np.int16);
          return audio;

      def _process(self, chunk):

          if chunk is not None:
             vad=self._vad.is_speech(chunk.tobytes(), self.context.default.AudioSampleRate);
          else:
             chunk=np.zeros(self._chunkSize, dtype=np.int16);
             vad=False;

          if   self._s == 0:
               if bool(vad) is False:
                  self._pattern.append('·');
                  self._s=0;
               else:
                  self._pattern.append('|');
                  self._buffer = chunk;
                  self._s=1;

          elif self._s == 1:
               if bool(vad) is False:
                  self._pattern.append('·');
                  self._buffer = np.concatenate((self._buffer, chunk));
                  self._s=2;
                  self._c=self._silence;
               else:
                  self._pattern.append('|');
                  self._buffer = np.concatenate((self._buffer, chunk));
                  self._s=1;

          elif self._s == 2:
               if bool(vad) is False:
                  if self._c==0:
                     if self._buffer.size < self._patience:
                        self._pattern.append('p');
                        self._buffer = np.concatenate((self._buffer, chunk));
                        self._s=1;
                     else:
                        self._buffer = np.concatenate((self._buffer, self.generate_tone(4, 5, 1)));
                        self.signal_segment(self._buffer);
                        self._pattern.append('#');
                        self.signal_pattern(''.join(self._pattern));
                        self._pattern=list();
                        self._buffer = np.ndarray(0, dtype=np.int16);
                        self._s=0;
                  else:
                     self._pattern.append('s');
                     self._buffer = np.concatenate((self._buffer, chunk));
                     self._s=2;
                     self._c-=1;
               else:
                  self._pattern.append('|');
                  self._buffer = np.concatenate((self._buffer, chunk));
                  self._s=1;

      @Block.slot("audio",{np.ndarray})
      def slot_audio(self, slot, data):
          if data is not None:

             if   np.issubdtype(data.dtype, np.integer):
                  scaled = np.interp(data, (data.min(), data.max()), (-2**15, 2**15-1));
                  audio=scaled.astype(np.int16);
             elif np.issubdtype(data.dtype, np.floating):
                  scaled = np.interp(data, (data.min(), data.max()), (-2**15, 2**15-1));
                  audio=scaled.astype(np.int16);
             else:
                  raise RuntimeError("Se esperaba un ndarray numérico, pero es de tipo", str(data.dtype));

             self._pattern= list();
             self._s      = 0;
             self._c      = 0;
             for i in range(math.ceil(audio.size/self._chunkSize)):
                 chunk=np.zeros(self._chunkSize, dtype=np.int16);
                 source  =audio[i*self._chunkSize:(i+1)*self._chunkSize];
                 chunk[:source.size]=source;
                 self._process(chunk);
             self._process(None);

      @Block.signal("segment",np.ndarray, sync=True)
      def signal_segment(self, data):
          return data;

      @Block.signal("pattern",str, sync=True)
      def signal_pattern(self, data):
          return data;
