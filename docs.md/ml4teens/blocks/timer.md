Module ml4teens.blocks.timer
============================

Classes
-------

`Timer(**kwargs)`
:   Emite la señal "event", 'times' veces (p.def. 10), cada 'interval' segundos (p.def. 1), con un valor dado como parámetro ("value") o el contador.
    SLOTS:   "times", "interval", "start" y "next".
    SIGNALS: "event" y "end"

    ### Ancestors (in MRO)

    * ml4teens.core.block.Block
    * abc.ABC

    ### Methods

    `signal_end(self, data='0c5a81d5f0f4027917f1007cf2f109535418afab60f805462711505e4f605178')`
    :

    `signal_event(self, data='3f9cf1f8add63a1b375faeda18cf2c38968896f8186dcc163db895a8d93c226e')`
    :

    `slot_interval(self, _slot, data)`
    :

    `slot_next(self, _slot, data)`
    :

    `slot_start(self, _slot, data)`
    :

    `slot_times(self, _slot, data)`
    :