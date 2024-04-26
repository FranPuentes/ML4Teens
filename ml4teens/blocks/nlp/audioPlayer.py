import gc;

import numpy       as np;
import sounddevice as sd;

from ...tools import tools;
from ...core  import Context;
from ...core  import Block;

class AudioPlayer(Block):

      def __init__(self, **kwargs):
          params, self._rest = tools.splitDict(["close","pause","play","autoplay"], **kwargs);
          super().__init__(**params);
          self._cache = [];
          self._offset=0;
          self._stream=None;
          self._paused=False;
          self._info  =None;

          import ipywidgets as widgets;
          from IPython.display import display;

          def create_button(text, color, fn):
              button = widgets.Button(description=text);
              button.style.button_color = color;         # Cambiar el color de fondo del botón
              button.style.font_weight = 'bold';         # Cambiar el peso de la fuente a negrita
              button.layout.width = '100px';             # Cambiar el ancho del botón
              button.layout.height = '40px';             # Cambiar la altura del botón
              button.layout.border = '2px solid black';  # Agregar un borde al botón
              button.on_click(fn);
              return button;

          self._buttons={"start":None, "pause":None, "stop":None };
          buttons=[];

          if bool(self.params.play) is True:
             text="▶ start";
             if self.params.play is str and len(self.params.play)>0:
                text=self.params.play;
             button = create_button(text,'lightcoral',lambda _: self._start());
             button.disabled=True;
             self._buttons["play"]=button;
             buttons.append(button);

          if bool(self.params.pause) is True:
             text="⏸ pause";
             if self.params.pause is str and len(self.params.pause)>0:
                text=self.params.pause;
             button = create_button(text,'lightcoral',lambda _: self._pause());
             button.disabled=True;
             self._buttons["pause"]=button;
             buttons.append(button);

          if bool(self.params.close) is True:
             text="⏹ stop";
             if self.params.close is str and len(self.params.close)>0:
                text=self.params.close;
             button = create_button(text,'coral',lambda _: self._stop());
             button.disabled=True;
             self._buttons["stop"]=button;
             buttons.append(button);

          if buttons:
             label = widgets.Label(value="AudioPlayer:");
             label.style.font_weight = 'bold';
             box = widgets.VBox([label,widgets.HBox(buttons)]);
             box.layout.border = '2px solid red';
             box.layout.padding = '10px';
             box.layout.margin = '10px';
             display(box);

      def _callback(self, outdata, frames, time, status):
          try:
              outdata[:]=0;

              if self._paused: return;

              if len(self._cache)>0:
                 cache=self._cache[0];
                 for off in range(frames):
                     outdata[off]=cache[self._offset];
                     self._offset+=1;
                     if self._offset >= cache.size:
                        self._cache.pop(0);
                        if len(self._cache)==0: raise sd.CallbackStop();
                        else:                   cache=self._cache[0];
                        self._offset=0;

              else:
                 raise sd.CallbackStop();

          except:
              self._offset=0;
              self._stream=None;
              self._buttons["play" ].disabled=True;
              self._buttons["pause"].disabled=True;
              self._buttons["stop" ].disabled=True;
              raise;

      def _start(self, data=None):
          if data is not None:
             if self._stream is None:
                self._offset=0;
                self._stream = sd.OutputStream(samplerate=self.context.default.AudioSampleRate, channels=1, dtype=data.dtype, callback=self._callback, blocksize=320*16);
             if not self._stream.active: self._stream.start();
             self._paused=False;
             self._buttons["play" ].disabled=True;
             self._buttons["pause"].disabled=False;
             self._buttons["stop" ].disabled=False;
             return self._stream.active if self._stream else False;

          else:
             self._pause();

      def _pause(self):
          if self._stream is not None:
             if self._paused:
                self._paused=False;
                self._buttons["play" ].disabled=True;
                self._buttons["pause"].disabled=False;
                self._buttons["stop" ].disabled=False;
                self._buttons["play" ].description="▶ start";
             else:
                self._paused=True;
                self._buttons["play" ].disabled=False;
                self._buttons["pause"].disabled=True;
                self._buttons["stop" ].disabled=False;
                self._buttons["play" ].description="▶ play";
             return self._paused;

      def _stop(self):
          if self._stream is not None:
             self._stream.abort();
             self._stream=None;
          self._buttons["play" ].disabled=True;
          self._buttons["pause"].disabled=True;
          self._buttons["stop" ].disabled=True;
          self._offset=0;
          self._paused=False;
          self._cache=[];
          gc.collect();
          return True;

      @Block.slot("segment",{np.ndarray})
      def slot_segment(self, slot, data):
          if data is not None:
             self._cache.append(data);
             if self.params.autoplay or True:
                self._start(data);
                return True;
          return False;

      @Block.slot("start",{object})
      def slot_start(self, slot, data):
          self._start();

      @Block.slot("pause",{object})
      def slot_pause(self, slot, data):
          self._pause();

      @Block.slot("stop",{object})
      def slot_stop(self, slot, data):
          self._stop();

