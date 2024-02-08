Module ml4teens.core.context
============================

Classes
-------

`Context()`
:   Este es un constructor falso, no hace nada.         
    La inicialización del **único** objeto de esta clase se hace en *__new__*.

    ### Class variables

    `Linker`
    :

    `instance`
    :

    ### Instance variables

    `allowGPU`
    :

    `fwd`
    :

    `gpu`
    :

    `gpus`
    :

    `mwd`
    :

    ### Methods

    `blocks(self)`
    :

    `checkSubscription(self, signal, slot=None)`
    :   Comprueba si se ha registrado la pareja (*signal*, *slot*) en este contexto.
        
        Si *slot* es None, sólo comprueba si está registrado *signal*.
        
        :param signal: La señal (*signal*).
        :type  signal: tupla (*block*, *signal name*)
        :param slot:   El *slot*.
        :type  slot:   tupla (*block*, *slot name*) | None
        :return:       Si *slot* no es None, devuelve si la pareja (*signal*,*slot*) está registrada. Si *slot* es None, devuelve si *signal* tiene *slot*s escuchando.
        :rtype:        True/False

    `emit(self, **kwargs)`
    :   Emite una señal directamente a los 'listeners' de (source,sname) o a un slot (target,sname).
        
        'target' y 'source' son exclusivos y obligatorios (por separado).
        
        :param source: El objeto que envía la señal.
        :type  source: Block
        :param target: El objeto al que se le envía la señal.
        :type  target: Block
        :param sname:  El nombre de una señal/slot (alias: signal_name o slot_name, según sea source/target).
        :type  sname:  str
        :param data:   El dato que acompaña a la señal.
        :type  data:   Cualquier cosa.
        :param mods:   Los modificadores, si se trata de el envío de un señal a un slot.
        :type  mods:   dict | None.

    `reset(self, all=False)`
    :

    `save(self, script_name, slots, signals=None)`
    :

    `subscribe(self, signal, slot, mods=({}, {}))`
    :   Registra la pareja (*signal*, *slot*) en este contexto.
        
        Si ya existe esta pareja, la elimina y la vuelve a añadir (quizá con otros *mods*).
        
        :param signal:   La señal (*signal*).
        :type  signal:   tupla (*block*, *signal name*)
        :param slot:     El *slot*.
        :type  slot:     Tupla (*block*, *slot name*)
        :param mods:     Modificadores de *signal*/*slot*.
        :type  mods:     dict*

    `unsubscribe(self, signal, slot)`
    :   Elimina la pareja (*signal*, *slot*) en este contexto.
        
        Si no existe esta pareja, no hace nada.
        
        :param signal: La señal (*signal*).
        :type  signal: tupla (*block*, *signal name*)
        :param slot:   El *slot*.
        :type  slot:   tupla (*block*, *slot name*)

    `wait(self, timeout=1)`
    :   Inicia el loop asíncrono y procesa los mensajes enviados por medio de la cola del contexto uno a uno.
        Se supone que el usuario ha colocado en la cola, previamente, mensajes para inicial la red.
        Si no hay mensajes en la cola, finaliza.
        Puede volver a invocarse, con nuevos mensajes encolados.