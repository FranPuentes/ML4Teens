Module ml4teens.blocks.ifElse
=============================

Classes
-------

`IfElse(**kwargs)`
:   Recibe en un slot llamado "event".
    Si cumple una condición, emite True por "true", en caso contrario False por "false".
    También emite True/False por la señal 'bool.
    La condición puede ser una lambda pasada por parámetro ("expression").
    La expresión también puede ser un texto, con un avariable local lamada 'data'.

    ### Ancestors (in MRO)

    * ml4teens.core.block.Block
    * abc.ABC

    ### Methods

    `signal_bool(self, data='ecc570cf2decd1dd5d2e97a8818ae56b834bb182228bf98ba4565ed9492482e8')`
    :

    `signal_false(self, data='ae60ee6dd66aec406fc3a75b12edf14a71f477e86c63d1957af6213fd238a63f')`
    :

    `signal_true(self, data='a8b17956cb9dc4e568b67eaada393c8dac312399eaa42c0a2b0d93085d3eedb0')`
    :

    `slot_event(self, _slot, data)`
    :