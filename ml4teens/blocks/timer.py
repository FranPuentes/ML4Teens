import time;

from ..core import Block;

class Timer(Block):
      """
      Emite la señal "event", 'times' veces (p.def. 10), cada 'interval' segundos (p.def. 1), con un valor dado como parámetro ("value") o el contador.
      SLOTS:   "times", "interval", "start" y "next".
      SIGNALS: "event" y "end"
      """

      #-------------------------------------------------------------------------
      # Constructor
      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          self._times   =self.params.times    if self.params.times    is not None else  10;
          self._interval=self.params.interval if self.params.interval is not None else 1.0;
          self._tm      =None;
          self._count   =None;

      #-------------------------------------------------------------------------
      # SLOTS
      #-------------------------------------------------------------------------
      @Block.slot("times",{int})
      def slot_times(self, slot, data:int):
          self._times=data if data is not None else 10;

      @Block.slot("interval",{float})
      def slot_interval(self, slot, data:float):
          self._interval=data if data is not None else 1.0;

      @Block.slot("start",{object})
      def slot_start(self, slot, data:object):
          self._count=1;
          self.signal_event(self.params.value if self.params.value is not None else self._count);
          self._tm=time.time();
          self._count += 1;

      @Block.slot("next",{object})
      def slot_next(self, slot, data:object):
          if self._count is None or self._tm is None:
             self._count=1;
             self._tm   =time.time();

          if self._count <= self._times:
             diff=(time.time()-self._tm);
             if diff > self._interval: pass;
             else:                     time.sleep(self._interval-diff);
             self.signal_event(self.params.value if self.params.value is not None else self._count);
             self._tm=time.time();
             self._count += 1;
          else:   
             self.signal_end(True);

      #-------------------------------------------------------------------------
      # SIGNALS
      #-------------------------------------------------------------------------
      @Block.signal("event",object)
      def signal_event(self, data):
          return data;

      @Block.signal("end",object)
      def signal_end(self, data):
          return data;

